import os
import re
from sqlalchemy.orm import Session
from fastapi import UploadFile
from pdf2image import convert_from_path

from app.schemas.lc import LCCreate
from app.repositories.lc_repo import LCRepo
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.core.config import settings
from app.services.ocr_service import ocr_image
from .parser import clean_text_common, clean_45a_text, extract_document_require_46A
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.services.audit_log_service import audit_log_service
import ollama
import json
import logging

logger = logging.getLogger(__name__)


def create_lc(db: Session, payload: LCCreate, user_id: int, pi_id: list[int]):
    # Check if LC with same lc_no already exists
    existing_lc = LCRepo.get_latest_version_by_lc_no(db, payload.lc_no)
    if existing_lc:
        # Increment version
        new_version = (existing_lc.versions or 0) + 1

        # Merge None fields from new payload with existing LC data
        payload_dict = payload.model_dump()

        for field, value in payload_dict.items():
            if value is None and hasattr(existing_lc, field):
                # If new value is None, use the old value
                old_value = getattr(existing_lc, field)
                setattr(payload, field, old_value)

        # Set the new version number
        payload.versions = new_version
    else:
        # First version
        payload.versions = 1
    transaction_ids = ProformaInvoiceRepo.get_transaction_by_pi_id(db, pi_id)
    lc = LCRepo.create(db, payload, user_id, pi_id)
    for transaction_id in transaction_ids:
        TransactionRepo.update(
            db,
            transaction_id,
            TransactionUpdate(status="completed", current_process="lc", lc_id=lc.id),
            user_id=user_id,
        )
        audit_log_service.log_action(db, "create", "lc", user_id, transaction_id)
    return lc


schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "item_no": {"type": "integer"},
            "description": {"type": ["string", "null"]},
        },
        "required": ["item_no", "description"],
    },
}


def call_qwen(prompt: str):
    response = ollama.chat(
        model="qwen2.5:7b-instruct",
        messages=[
            {
                "role": "user",
                "content": f"""
            คุณเป็นผู้ช่วยดึงข้อมูลจาก Letter of Credit (LC) field 45A: DESCRIPTION OF GOODS AND/OR SERVICES
นี่คือเนื้อหา 45A:
{prompt}
คำสั่ง:
1. ดึงรายการสินค้า/รถแต่ละรายการออกมาเป็น JSON
2. แต่ละ item ต้องมี fields:
- item_no: เลขลำดับรายการ (เช่น 1, 2, 3…)
- description: รายละเอียดของรถ
3. ถ้า field ไหนไม่มี ให้ใช้ค่า null
4. คืนค่าผลลัพธ์เป็น JSON ล้วน ไม่ต้องมีข้อความอื่น
5. ลำดับ item ต้องตรงตามที่ปรากฏใน text

ตัวอย่าง output:
[
{{
"item_no": 1,
"description": "1) ONE UNIT OF USED HONDA CITY 1.0RS VTEC TURBO AUTO
YEAR OF MANUFACTURE: 2025
CHASSIS: MRHGN1680ST102773 WLT018
H.S. CODE: 8703.21.69
UNIT PRICE: USD 13,500",
}},
{{
"item_no": 2,
"description": "2) ONE UNIT OF USED HONDA CITY 1.0RS VTEC TURBO AUTO\nYEAR OF MANUFACTURE: 2025\nCHASSIS: MRHGN1680ST102248 WLT019\nH.S. CODE: 8703.21.69 UNIT PRICE: USD 13,500",
}},
]     
            """,
            },
        ],
        options={"temperature": 0},
        format=schema,
    )
    content = response["message"]["content"]
    return content


#     review_prompt = f"""
# นี่คือ JSON ที่คุณดึงมา:
# {content}

# ORIGINAL DATA
# {prompt}
# ตรวจสอบว่าครบทุก item, ลำดับถูกต้อง, มี H.S. CODE ทุก item
# ถ้ามี missing ให้เติม null
# ส่ง JSON array ใหม่
# """
#     review_response = ollama.chat(
#         model="qwen2.5:7b-instruct",
#         messages=[{"role": "user", "content": review_prompt}],
#         options={"temperature": 0},
#     )

#     return review_response["message"]["content"]


def extract_lc(db: Session, file: UploadFile, user_id: int, transaction_id: int):
    """
    Extract LC data from PDF file and return as JSON
    """
    # Save uploaded file
    upload_dir = "app/pdf"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    PDF_PATH = file_path
    POPPLER_PATH = settings.POPPLER_PATH

    # Convert PDF to images (all pages)
    pages = convert_from_path(PDF_PATH, dpi=300, poppler_path=POPPLER_PATH)

    results = []
    for idx, page in enumerate(pages):
        print(f"OCR page {idx + 1}/{len(pages)}")
        text = ocr_image(page)
        results.append({"page": idx + 1, "text": text.strip()})

    # Combine all text
    full_text = "\n\n".join(f"[Page {r['page']}]\n{r['text']}" for r in results)
    # Extract all fields using regex
    extracted_data = {
        "sequence_of_total_27": re.search(
            r"SEQUENCE\s*OF\s*TOTAL\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "form_of_documentary_credit_40a": re.search(
            r"FORM\s*OF\s*DOCUMENTARY\s*CREDIT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "docmentary_credit_number_20": re.search(
            r"DOCUMENTARY\s*CREDIT\s*NUMBER\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "date_of_issue_31c": re.search(
            r"DATE\s*OF\s*ISSUE\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "applicable_rules_40e": re.search(
            r"APPLICABLE\s*RULES\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "date_and_place_of_expiry_31d": re.search(
            r"DATE\s*AND\s*PLACE\s*OF\s*EXPIRY\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "applicant_50": re.search(
            r"APPLICANT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "beneficiary_59": re.search(
            r"59:\s*BENEFICIARY\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "currency_code_32b": re.search(
            r"32B:\s*CURRENCY\s*CODE\s*,\s*AMOUNT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "available_with_41d": re.search(
            r"AVAILABLE\s*WITH\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "partial_shipments_43p": re.search(
            r"PARTIAL\s*SHIPMENTS\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "transhipment_43t": re.search(
            r"TRANSHIPMENT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "port_of_loading_of_departure_44e": re.search(
            r"PORT\s*OF\s*LOADING/AIRPORT\s*OF\s*DEPARTURE\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "port_of_discharge_44f": re.search(
            r"PORT\s*OF\s*DISCHARGE/AIRPORT\s*OF\s*DESTINATION\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "latest_date_of_shipment_44c": re.search(
            r"LATEST\s*DATE\s*OF\s*SHIPMENT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "additional_conditions_47a": re.search(
            r"47A\s*:\s*ADDITIONAL\s*CONDITIONS\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "charges_71d": re.search(
            r"71D\s*:\s*CHARGES\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL | re.IGNORECASE
        ),
        "period_for_presentation_in_days_48": re.search(
            r"PERIOD\s*FOR\s*PRESENTATION\s*IN\s*DAYS\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "confirmation_instructions_49": re.search(
            r"CONFIRMATION\s*INSTRUCTIONS\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "instructions_to_the_paying_accepting_negotiating_bank_78": re.search(
            r"INSTRUCTIONS\s*TO\s*THE\s*PAYING/ACCEPTING/NEGOTIATING\s*BANK\s*(.*?)(?=THIS CREDIT IS VALID ONLY WHEN USED)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "lc_no": re.search(
            r"LC\s*ADVICE\s*NO.\s*(.+?)(?=\s*DATE)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "number_of_amendment_26e": re.search(
            r"NUMBER\s*OF\s*AMENDMENT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "date_of_amendment_30": re.search(
            r"DATE\s*OF\s*AMENDMENT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "applicant_bank_51d": re.search(
            r"51D\s*:\s*APPLICANT\s*BANK\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "drafts_at_42c": re.search(
            r"42C\s*:\s*DRAFTS\s*AT\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "drawee_42a": re.search(
            r"42A\s*:\s*DRAWEE\s*(.+?)(?=\s*:|$)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "sender_reference_20": re.search(
            r":20:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "receiver_reference_21": re.search(
            r":21:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "issuing_bank_reference_23": re.search(
            r":23:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "issuing_bank_52a": re.search(
            r":52A:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "purpose_of_message_22a": re.search(
            r":22A:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
        "additional_conditions_47b": re.search(
            r":47B:\s*(.*?)\s*(?=\n:\d{2}[A-Z]?:|\Z)",
            full_text,
            re.DOTALL | re.IGNORECASE,
        ),
    }
    result_text = ""
    match_45B = re.search(r"45B", full_text)
    logger.debug(f"[LC] Match 45B : {match_45B}")
    if match_45B:
        start_idx = match_45B.start()
        hs_matches = list(re.finditer(r"H\.S\.", full_text))
        last_hs = hs_matches[-1].end()  # เอา index หลัง H.S. ตัวสุด
        end_idx = min(
            last_hs + 30, len(full_text)
        )  # +30 ตัวอักษร และไม่เกินความยาว string # 3. ดึง substring
        result_text = full_text[start_idx:end_idx]
    else:
        match_45A = re.search(r"\s*45\s*A[:\)]?", full_text)
        if match_45A:
            start_idx = match_45A.start()
            hs_matches = list(re.finditer(r"H\.S\.", full_text))
            last_hs = hs_matches[-1].end()  # เอา index หลัง H.S. ตัวสุด
            end_idx = min(
                last_hs + 30, len(full_text)
            )  # +30 ตัวอักษร และไม่เกินความยาว string # 3. ดึง substring
            result_text = full_text[start_idx:end_idx]
    logger.debug(f"[LC] Result text : {result_text}")
    logger.debug(f"[LC] Full text preview : {full_text}")
    # Build description_of_good_45a_45b as JSON with items
    description_of_good_45a_45b = None
    llm_output = call_qwen(result_text)
    # ดึงเฉพาะ JSON array
    match = re.search(r"\[.*\]", llm_output, re.DOTALL)
    # logger.debug(f"[LC] LLM output : {llm_output}")
    # logger.debug(f"[LC] Match : {match}")
    if match:
        json_text = match.group(0)
        try:
            description_of_good_45a_45b = json.loads(json_text)
            allowed_keys = {"item_no", "description"}
            for item in description_of_good_45a_45b:
                keys_to_remove = set(item.keys()) - allowed_keys
                for k in keys_to_remove:
                    item.pop(k)
        except Exception as e:
            print("JSON PARSE ERROR:", e)
            print(json_text)
            description_of_good_45a_45b = None
    else:
        print("NO JSON FOUND")
        print(llm_output)
        description_of_good_45a_45b = None
    document_require_46a = extract_document_require_46A(full_text)
    # Build response JSON
    response_data = {
        "beneficiary_59": extracted_data["beneficiary_59"].group(1).strip()
        if extracted_data["beneficiary_59"]
        else None,
        "applicant_50": extracted_data["applicant_50"].group(1).strip()
        if extracted_data["applicant_50"]
        else None,
        "description_of_good_45a_45b": description_of_good_45a_45b,
        "date_of_issue_31c": extracted_data["date_of_issue_31c"].group(1).strip()
        if extracted_data["date_of_issue_31c"]
        else None,
        "lc_no": extracted_data["lc_no"].group(1).strip()
        if extracted_data["lc_no"]
        else None,
        "document_require_46a": document_require_46a if document_require_46a else None,
        "docmentary_credit_number_20": extracted_data["docmentary_credit_number_20"]
        .group(1)
        .strip()
        if extracted_data["docmentary_credit_number_20"]
        else None,
        "sequence_of_total_27": extracted_data["sequence_of_total_27"].group(1).strip()
        if extracted_data["sequence_of_total_27"]
        else None,
        "form_of_documentary_credit_40a": extracted_data[
            "form_of_documentary_credit_40a"
        ]
        .group(1)
        .strip()
        if extracted_data["form_of_documentary_credit_40a"]
        else None,
        "applicable_rules_40e": extracted_data["applicable_rules_40e"].group(1).strip()
        if extracted_data["applicable_rules_40e"]
        else None,
        "date_and_place_of_expiry_31d": extracted_data["date_and_place_of_expiry_31d"]
        .group(1)
        .strip()
        if extracted_data["date_and_place_of_expiry_31d"]
        else None,
        "currency_code_32b": extracted_data["currency_code_32b"].group(1).strip()
        if extracted_data["currency_code_32b"]
        else None,
        "available_with_41d": extracted_data["available_with_41d"].group(1).strip()
        if extracted_data["available_with_41d"]
        else None,
        "partial_shipments_43p": extracted_data["partial_shipments_43p"]
        .group(1)
        .strip()
        if extracted_data["partial_shipments_43p"]
        else None,
        "transhipment_43t": extracted_data["transhipment_43t"].group(1).strip()
        if extracted_data["transhipment_43t"]
        else None,
        "port_of_discharge_44f": extracted_data["port_of_discharge_44f"]
        .group(1)
        .strip()
        if extracted_data["port_of_discharge_44f"]
        else None,
        "port_of_loading_of_departure_44e": extracted_data[
            "port_of_loading_of_departure_44e"
        ]
        .group(1)
        .strip()
        if extracted_data["port_of_loading_of_departure_44e"]
        else None,
        "latest_date_of_shipment_44c": extracted_data["latest_date_of_shipment_44c"]
        .group(1)
        .strip()
        if extracted_data["latest_date_of_shipment_44c"]
        else None,
        "charges_71d": extracted_data["charges_71d"].group(1).strip()
        if extracted_data["charges_71d"]
        else None,
        "additional_conditions_47a": (
            clean_text_common(extracted_data["additional_conditions_47a"].group(1))
            if extracted_data["additional_conditions_47a"]
            else None
        ),
        "period_for_presentation_in_days_48": extracted_data[
            "period_for_presentation_in_days_48"
        ]
        .group(1)
        .strip()
        if extracted_data["period_for_presentation_in_days_48"]
        else None,
        "confirmation_instructions_49": extracted_data["confirmation_instructions_49"]
        .group(1)
        .strip()
        if extracted_data["confirmation_instructions_49"]
        else None,
        "instructions_to_the_paying_accepting_negotiating_bank_78": extracted_data[
            "instructions_to_the_paying_accepting_negotiating_bank_78"
        ]
        .group(1)
        .strip()
        if extracted_data["instructions_to_the_paying_accepting_negotiating_bank_78"]
        else None,
        "number_of_amendment_26e": extracted_data["number_of_amendment_26e"]
        .group(1)
        .strip()
        if extracted_data["number_of_amendment_26e"]
        else None,
        "date_of_amendment_30": extracted_data["date_of_amendment_30"].group(1).strip()
        if extracted_data["date_of_amendment_30"]
        else None,
        "applicant_bank_51d": extracted_data["applicant_bank_51d"].group(1).strip()
        if extracted_data["applicant_bank_51d"]
        else None,
        "drafts_at_42c": extracted_data["drafts_at_42c"].group(1).strip()
        if extracted_data["drafts_at_42c"]
        else None,
        "drawee_42a": extracted_data["drawee_42a"].group(1).strip()
        if extracted_data["drawee_42a"]
        else None,
        "sender_reference_20": extracted_data["sender_reference_20"].group(1).strip()
        if extracted_data["sender_reference_20"]
        else None,
        "receiver_reference_21": extracted_data["receiver_reference_21"]
        .group(1)
        .strip()
        if extracted_data["receiver_reference_21"]
        else None,
        "issuing_bank_52a": extracted_data["issuing_bank_52a"].group(1).strip()
        if extracted_data["issuing_bank_52a"]
        else None,
        "purpose_of_message_22a": extracted_data["purpose_of_message_22a"]
        .group(1)
        .strip()
        if extracted_data["purpose_of_message_22a"]
        else None,
        "additional_conditions_47b": extracted_data["additional_conditions_47b"]
        .group(1)
        .strip()
        if extracted_data["additional_conditions_47b"]
        else None,
        "pdf_path": file_path,
        "text": full_text,
    }
    TransactionRepo.update(
        db,
        transaction_id,
        TransactionUpdate(status="pending", current_process="lc"),
        user_id=user_id,
    )
    audit_log_service.log_action(db, "extract", "lc", user_id, transaction_id)
    return response_data
