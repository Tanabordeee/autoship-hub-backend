import os
import re
from sqlalchemy.orm import Session
from fastapi import UploadFile
from pdf2image import convert_from_path

from app.schemas.lc import LCCreate
from app.repositories.lc_repo import LCRepo
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from .ocr import ocr_image
from .parser import clean_text_common, clean_45a_text, extract_document_require_46A


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

    return LCRepo.create(db, payload, user_id, pi_id)


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
    MODEL = "scb10x/typhoon-ocr1.5-3b:latest"
    POPPLER_PATH = r"E:\poppler\poppler-25.12.0\Library\bin"

    # Convert PDF to images (all pages)
    pages = convert_from_path(PDF_PATH, dpi=300, poppler_path=POPPLER_PATH)

    results = []
    for idx, page in enumerate(pages):
        print(f"OCR page {idx + 1}/{len(pages)}")
        text = ocr_image(page, MODEL)
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
    }

    # Extract description of goods
    description_match = re.search(
        r"45A\s*:\s*DESCRIPTION\s*OF\s*GOODS\s*AND/OR\s*SERVICES\s*(.+?)(?=\s*\n?\s*\d{2}[A-Z]?\s*:|$)",
        full_text,
        re.DOTALL | re.IGNORECASE,
    )

    # Build description_of_good_45a_45b as JSON with items
    description_of_good_45a_45b = None
    if description_match:
        raw_description_text = description_match.group(1).strip()
        description_text = clean_45a_text(raw_description_text)
        # Extract individual items (UNIT)
        items = re.split(
            r"(?=\b\d{1,2}\s+UNIT\b)", description_text, flags=re.IGNORECASE
        )
        items = [i.strip() for i in items if i.strip()]
        description_of_good_45a_45b = {
            "full_text": description_text,
            "items": [
                {"item_no": idx + 1, "description": item.strip()}
                for idx, item in enumerate(items)
            ]
            if items
            else [],
        }
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
        "pdf_path": file_path,
    }
    TransactionRepo.update(
        db, transaction_id, TransactionUpdate(status="pending", current_process="lc")
    )
    return response_data
