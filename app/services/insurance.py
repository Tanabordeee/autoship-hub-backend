from app.services.ocr_service import extract_text_from_file
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import ollama


class InsuranceHeader(BaseModel):
    name: Optional[str] = None
    certificate_no: Optional[str] = None
    name_of_insured: Optional[str] = None
    vessle: Optional[str] = None
    sailing_on_or_about: Optional[str] = None
    voyage: Optional[str] = None
    subject_matter_insured: Optional[str] = None


class InsuranceDetails(BaseModel):
    additional_conditional: Optional[str] = None
    special_conditional_and_warranties: Optional[str] = None
    invoice_no: Optional[str] = None
    chassis_no: Optional[str] = None
    engine: Optional[str] = None
    the_letter_of_credit_number: Optional[str] = None
    date_of_issue: Optional[str] = None
    bank: Optional[str] = None
    Date: Optional[str] = None


def call_gemma_Header(PROMPT):
    response = ollama.chat(
        model="gemma3:27b-it-qat",
        messages=[
            {
                "role": "system",
                "content": "คุณคือนักจัดการ insurance document ช่วยดึงข้อมูลออกมาใส่ตามเป็น value ให้ key เหล่านี้ โดยห้ามคิดเอาเองให้อิงตาม input user อันไหนที่ไม่รู้ไม่แน่ใจให้ใส่เป็น null และแสดงผลออกมาเป็นรูปแบบ json นี้เท่านั้น copy text verbatim between the heading and next heading",
            },
            {"role": "user", "content": PROMPT},
        ],
        options={"temperature": 0},
        format=InsuranceHeader.model_json_schema(),
    )
    content = response["message"]["content"]
    return InsuranceHeader.model_validate_json(content).model_dump()


def call_gemma_Details(PROMPT):
    response = ollama.chat(
        model="gemma3:27b-it-qat",
        messages=[
            {
                "role": "system",
                "content": "คุณคือนักจัดการ insurance document ช่วยดึงข้อมูลออกมาใส่ตามเป็น value ให้ key เหล่านี้ โดยห้ามคิดเอาเองให้อิงตาม input user อันไหนที่ไม่รู้ไม่แน่ใจให้ใส่เป็น null และแสดงผลออกมาเป็นรูปแบบ json นี้เท่านั้น copy text verbatim between the heading and next heading",
            },
            {"role": "user", "content": PROMPT},
        ],
        options={"temperature": 0},
        format=InsuranceDetails.model_json_schema(),
    )
    content = response["message"]["content"]
    return InsuranceDetails.model_validate_json(content).model_dump()


def merge_dicts(a: dict, b: dict) -> dict:
    result = {}
    for key in set(a) | set(b):
        if key in a and a[key] not in [None, ""]:
            result[key] = a[key]
        else:
            result[key] = b.get(key)
    return result


def extract_insurance(db: Session, file):
    raw_text = extract_text_from_file(file)
    PROMPT1 = f"""
    USER INPUT
    {raw_text}
    RULES:
    - Output JSON ONLY
    - You MUST output ALL keys
    - If not found, output null explicitly
    - DO NOT rename keys
    - Copy text verbatim between the heading and next heading
    {{
    name : บริษัทประกัน เช่น MSIG Insurance (Thailand) Public Company Limited,
    certificate_no : มักขึ้นต้นด้วย Certificate\s+No แล้วตามหลังด้วยเลข,
    name_of_insured : มักขึ้นต้นด้วย NAME\s+OF\s+INSURED,
    vessle : มักขึ้นต้นด้วย VESSEL\/CONVEYANCE,
    sailing_on_or_about : มักขึ้นต้นด้วย SAILING\s+ON\s+OR\s+ABOUT แล้วตามด้วย วันเดือนปี,
    voyage : มักขึ้นต้นด้วย VOYAGE\s*:\s*(.+),
    subject_matter_insured : Extract verbatim text starting from the first line under
    "SUBJECT-MATTER INSURED:" in the ATTACHMENT section.
    STOP extraction immediately after the line that contains
    "H.S. CODE" or "H. S. CODE".
    Do NOT include any text after the H.S. CODE line
    มักขึ้นต้นด้วย SUBJECT[\s\-]*MATTER\s+INSURED
    }}
    """
    PROMPT2 = f"""
    USER INPUT
    {raw_text}
    RULES:
    - Output JSON ONLY
    - You MUST output ALL keys
    - If not found, output null explicitly
    - DO NOT rename keys
    - Copy text verbatim between the heading and next heading
    {{
    additional_conditional : มักมีคำขึ้นต้นด้วย ADDITIONAL CONDITIONALS
    special_conditional_and_warranties: มักมีคำขึ้นต้นด้วย SPECIAL\s+CONDITIONS\s+AND\s+WARRANTIES,
    invoice_no : มักจะขึ้นต้นด้วย PROFORMA\s+INVOICE\s+NO\.?\s*[:\-]?\s*([A-Z0-9\-]+)
    chassis_no : มักขึ้นต้นด้วย CHASSIS\s+NO\.?\s*[:\-]?\s*([A-Z0-9]+),
    engine : มักขึ้นต้นด้วย ENGINE\s*[:\-]?\s*([A-Z0-9]+) ,
    the_letter_of_credit_number : มักขึ้นต้นด้วย LETTER\s+OF\s+CREDIT\s+NUMBER\.?\s*[:\-]?\s*([0-9]+),
    date_of_issue : มักขึ้นต้นด้วย DATE\s+OF\s+ISSUE\s*[:\-]?\s*([0-9]+),
    bank : มักขึ้นต้นด้วย (PEOPLE'S\s+BANK[\s\S]*?SRI\s+LANKA\.?)
    Date : มักขึ้นต้นด้วย Date,
    }}
    """
    result_1 = call_gemma_Header(PROMPT1)
    result_2 = call_gemma_Details(PROMPT2)

    final_result = merge_dicts(result_1, result_2)
    return final_result
