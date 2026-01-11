from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
import base64
import requests
import io
from pdf2image import convert_from_path
from app.schemas.lc import LCCreate
from app.repositories.lc_repo import LCRepo
import re
def ocr_image(image, model: str):
    """Helper function to OCR a single image"""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode()

    payload = {
        "model": model,
        "prompt": "อ่านข้อความทั้งหมดในภาพนี้อย่างละเอียด\n- รักษาลำดับบรรทัด\n- ไม่สรุป\n- ไม่ตีความ\n- พิมพ์ตามต้นฉบับ 100%",
        "images": [img_base64],
        "stream": False
    }

    r = requests.post(
        "http://localhost:11434/api/generate",
        json=payload
    )
    
    try:
        data = r.json()
        if "response" in data:
            return data["response"]
        else:
            print(f"Error: 'response' key missing. API returned: {data}")
            return f"[Error: {data.get('error', 'Unknown error')}]"
    except Exception as e:
        print(f"Exception during JSON parsing: {e}")
        print(f"Status Code: {r.status_code}")
        print(f"Raw Response: {r.text}")
        return "[Error: Failed to parse response]"

def extract_lc(db: Session, file: UploadFile, user_id: int):
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
        print(f"OCR page {idx+1}/{len(pages)}")
        text = ocr_image(page, MODEL)
        results.append({"page": idx + 1, "text": text.strip()})

    # Combine all text
    full_text = "\n\n".join(f"[Page {r['page']}]\n{r['text']}" for r in results)
    
    # Extract all fields using regex
    extracted_data = {
        "sequence_of_total_27": re.search(r"SEQUENCE\s*OF\s*TOTAL\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "form_of_documentary_credit_40a": re.search(r"FORM\s*OF\s*DOCUMENTARY\s*CREDIT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "docmentary_credit_number_20": re.search(r"DOCUMENTARY\s*CREDIT\s*NUMBER\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "date_of_issue_31c": re.search(r"DATE\s*OF\s*ISSUE\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "applicable_rules_40e": re.search(r"APPLICABLE\s*RULES\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "date_and_place_of_expiry_31d": re.search(r"DATE\s*AND\s*PLACE\s*OF\s*EXPIRY\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "applicant_50": re.search(r"APPLICANT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "beneficiary_59": re.search(r"59:\s*BENEFICIARY\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "currency_code_32b": re.search(r"32B:\s*CURRENCY\s*CODE\s*,\s*AMOUNT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "available_with_41d": re.search(r"AVAILABLE\s*WITH\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "partial_shipments_43p": re.search(r"PARTIAL\s*SHIPMENTS\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "transhipment_43t": re.search(r"TRANSHIPMENT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "port_of_loading_of_departure_44e": re.search(r"PORT\s*OF\s*LOADING/AIRPORT\s*OF\s*DEPARTURE\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "port_of_discharge_44f": re.search(r"PORT\s*OF\s*DISCHARGE/AIRPORT\s*OF\s*DESTINATION\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "latest_date_of_shipment_44c": re.search(r"LATEST\s*DATE\s*OF\s*SHIPMENT\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "additional_conditions_47a": re.search(r"47A\s*:\s*ADDITIONAL\s*CONDITIONS\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "charges_71d": re.search(r"71D\s*:\s*CHARGES\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "period_for_presentation_in_days_48": re.search(r"PERIOD\s*FOR\s*PRESENTATION\s*IN\s*DAYS\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "confirmation_instructions_49": re.search(r"CONFIRMATION\s*INSTRUCTIONS\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
        "instructions_to_the_paying_accepting_negotiating_bank_78": re.search(r"INSTRUCTIONS\s*TO\s*THE\s*PAYING/ACCEPTING/NEGOTIATING\s*BANK\s*(.*?)(?=THIS CREDIT IS VALID ONLY WHEN USED)", full_text, re.DOTALL|re.IGNORECASE),
        "lc_no": re.search(r"LC\s*ADVICE\s*NO.\s*(.+?)(?=\s*DATE)", full_text, re.DOTALL|re.IGNORECASE),
    }
    
    # Extract description of goods
    description_match = re.search(r"45A\s*:\s*DESCRIPTION\s*OF\s*GOODS\s*AND/OR\s*SERVICES\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE)
    
    # Extract documents required
    docs_46a = {
        "1": re.search(r"46A\s*:\s*DOCUMENTS\s*REQUIRED\s*(.+?)(?=\s*\n?\s*2\))", full_text, re.DOTALL|re.IGNORECASE),
        "2": re.search(r"2\)\s*(FULL\s*SET\s*OF.+?)(?=\s*\n?\s*3\))", full_text, re.DOTALL|re.IGNORECASE),
        "3": re.search(r"3\)\s*(.+?)(?=\s*4\))", full_text, re.DOTALL|re.IGNORECASE),
        "4": re.search(r"4\)\s*(.+?)(?=\s*5\))", full_text, re.DOTALL|re.IGNORECASE),
        "5": re.search(r"5\)\s*(.+?)(?=\s*6\))", full_text, re.DOTALL|re.IGNORECASE),
        "6": re.search(r"6\)\s*(.+?)(?=\s*7\))", full_text, re.DOTALL|re.IGNORECASE),
        "7": re.search(r"7\)\s*(.+?)(?=\s*:|$)", full_text, re.DOTALL|re.IGNORECASE),
    }
    
    # Build document_require_46a as JSON with cleanup for item 3
    document_require_46a = {}
    for key, match in docs_46a.items():
        if match:
            item_text = match.group(1).strip()
            
            # Special cleanup for item 3 (insurance documents)
            if key == "3":
                item_text = re.sub(
                    r"THIS CREDIT IS VALID ONLY WHEN USED.*?(?=\n)|"
                    r"NOTIFICATION OF LC ADVICE.*?(?=\n)|"
                    r"PAGE \d+/.*?(?=\n)|"
                    r"\[Page \d+\].*?(?=\n)|"
                    r"^standard chartered\s*$|"
                    r"^COMMERCIAL BANK OF CEYLON PLC\s*$|"
                    r"^SH REL.*?(?=\n)|"
                    r".*?ARR \.DATE=.*?(?=\n)|"
                    r".*?ARR \.TIME=.*?(?=\n)|"
                    r".*?REF \.NO\..*?(?=\n)|"
                    r"^ARR .*?(?=\n)|"
                    r"^REF .*?(?=\n)|"
                    r"^DEAL=.*?(?=\n)|"
                    r"^SENDER:.*?(?=\n)|"
                    r".*?TEST AGREED SENDER.*?(?=\n)|"
                    r"^Tel .*?(?=\n)|"
                    r"^Fax .*?(?=\n)|"
                    r"^Registration .*?(?=\n)|"
                    r"^โทรศัพท์ .*?(?=\n)|"
                    r"^โทรสาร .*?(?=\n)|"
                    r"^ทะเบียนเลขที่ .*?(?=\n)|"
                    r"^ธนาคารสแตนดาร์ดชาร์เตอร์ด.*?(?=\n)|"
                    r"^140 ถนน.*?(?=\n)|"
                    r"^140 Wireless.*?(?=\n)|"
                    r"^ITSD-14.*?(?=\n)|"
                    r"^\d+\s+TEST AGREED.*?(?=\n)|"
                    r"^\d+\s*$|"
                    r"^COLOMBO\s*$|"
                    r"^Bangkok \d+.*?(?=\n)|"
                    r"Standard Chartered Bank.*?(?=\n)",
                    "",
                    item_text,
                    flags=re.IGNORECASE | re.MULTILINE
                )
                # Remove duplicate newlines
                item_text = re.sub(r'\n\s*\n+', '\n', item_text).strip()
            
            document_require_46a[key] = item_text
    
    # Extract annexures from item 6 if available
    if "6" in document_require_46a:
        annexures = re.findall(r"(\([A-Z]+\))\s*(.+?)(?=(\([A-Z]+\)|$))", document_require_46a["6"], re.DOTALL)
        if annexures:
            document_require_46a["6_annexures"] = [{"label": a[0], "text": a[1].strip()} for a in annexures]
    
    # Build description_of_good_45a_45b as JSON with items
    description_of_good_45a_45b = None
    if description_match:
        description_text = description_match.group(1).strip()
        
        # Extract individual items (UNIT)
        items = re.findall(
            r"(\d{1,2}\s*UNIT.*?(?:H\. ?S\. ?CODE\s*\.\s*\d+\.\d+\.\d+|UNIT PRICE\s*:\s*USD[\d,]+|$))",
            description_text,
            re.DOTALL | re.IGNORECASE
        )
        
        description_of_good_45a_45b = {
            "full_text": description_text,
            "items": [item.strip() for item in items] if items else []
        }

    # Build response JSON
    response_data = {
        "beneficiary_59": extracted_data["beneficiary_59"].group(1).strip() if extracted_data["beneficiary_59"] else None,
        "applicant_50": extracted_data["applicant_50"].group(1).strip() if extracted_data["applicant_50"] else None,
        "description_of_good_45a_45b": description_of_good_45a_45b,
        "date_of_issue_31c": extracted_data["date_of_issue_31c"].group(1).strip() if extracted_data["date_of_issue_31c"] else None,
        "lc_no": extracted_data["lc_no"].group(1).strip() if extracted_data["lc_no"] else None,
        "document_require_46a": document_require_46a if document_require_46a else None,
        "docmentary_credit_number_20": extracted_data["docmentary_credit_number_20"].group(1).strip() if extracted_data["docmentary_credit_number_20"] else None,
        "sequence_of_total_27": extracted_data["sequence_of_total_27"].group(1).strip() if extracted_data["sequence_of_total_27"] else None,
        "form_of_documentary_credit_40a": extracted_data["form_of_documentary_credit_40a"].group(1).strip() if extracted_data["form_of_documentary_credit_40a"] else None,
        "applicable_rules_40e": extracted_data["applicable_rules_40e"].group(1).strip() if extracted_data["applicable_rules_40e"] else None,
        "date_and_place_of_expiry_31d": extracted_data["date_and_place_of_expiry_31d"].group(1).strip() if extracted_data["date_and_place_of_expiry_31d"] else None,
        "currency_code_32b": extracted_data["currency_code_32b"].group(1).strip() if extracted_data["currency_code_32b"] else None,
        "available_with_41d": extracted_data["available_with_41d"].group(1).strip() if extracted_data["available_with_41d"] else None,
        "partial_shipments_43p": extracted_data["partial_shipments_43p"].group(1).strip() if extracted_data["partial_shipments_43p"] else None,
        "transhipment_43t": extracted_data["transhipment_43t"].group(1).strip() if extracted_data["transhipment_43t"] else None,
        "port_of_discharge_44f": extracted_data["port_of_discharge_44f"].group(1).strip() if extracted_data["port_of_discharge_44f"] else None,
        "port_of_loading_of_departure_44e": extracted_data["port_of_loading_of_departure_44e"].group(1).strip() if extracted_data["port_of_loading_of_departure_44e"] else None,
        "latest_date_of_shipment_44c": extracted_data["latest_date_of_shipment_44c"].group(1).strip() if extracted_data["latest_date_of_shipment_44c"] else None,
        "charges_71d": extracted_data["charges_71d"].group(1).strip() if extracted_data["charges_71d"] else None,
        "additional_conditions_47a": extracted_data["additional_conditions_47a"].group(1).strip() if extracted_data["additional_conditions_47a"] else None,
        "period_for_presentation_in_days_48": extracted_data["period_for_presentation_in_days_48"].group(1).strip() if extracted_data["period_for_presentation_in_days_48"] else None,
        "confirmation_instructions_49": extracted_data["confirmation_instructions_49"].group(1).strip() if extracted_data["confirmation_instructions_49"] else None,
        "instructions_to_the_paying_accepting_negotiating_bank_78": extracted_data["instructions_to_the_paying_accepting_negotiating_bank_78"].group(1).strip() if extracted_data["instructions_to_the_paying_accepting_negotiating_bank_78"] else None,
        "pdf_path": file_path,
    }
    
    return response_data
