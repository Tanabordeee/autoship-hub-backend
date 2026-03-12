import re
import json
from openai import OpenAI
from app.core.config import settings

if settings.DEMO == 1:
    # Initialize Typhoon Client
    client = OpenAI(
        api_key=settings.TYPHOON_API_KEY, base_url=settings.TYPHOON_CHAT_URL
    )
else:
    import ollama


def clean_text_common(text: str) -> str:
    text = re.sub(
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
        r"Standard Chartered Bank.*?(?=\n)|"
        r"TEST AGREED COMMERCIAL BANK OF CEYLON PLC COLOMBO.*?(?=\n)|"
        r"ICC PUBLICATION NO\.600 IS EXCLUDED.*?(?=\n)|"
        r"ARTICLE\s+\d+.*?UCP.*?(?=\n)|",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text


def clean_45a_text(text: str) -> str:
    # ตัดทุกอย่างหลัง noise marker (STOP WORDS)
    stop_patterns = [
        r"THIS CREDIT IS VALID ONLY WHEN USED",
        r"NOTIFICATION OF LC ADVICE",
        r"PAGE\s+\d+/",
        r"\[Page\s*\d+\]",
        r"Standard Chartered Bank",
        r"ธนาคารสแตนดาร์ดชาร์เตอร์ด",
        r"COMMERCIAL BANK OF CEYLON",
        r"COMERCIAL BANK OF CEYLON",
        r"SH REL\. DATE",
        r"SENDER:",
    ]

    for p in stop_patterns:
        text = re.split(p, text, flags=re.IGNORECASE)[0]

    # cleanup whitespace
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text


def extract_swift_field(full_text: str):
    """
    Extract a SWIFT MT700 field block using regex.
    Example: field_tag = "46A"
    """
    # Robust regex for SWIFT fields like :46A: or : 46A:
    pattern = rf"\s:?\s*46A\s*:\s*(.*?)(?=\s:\s*\d{2}[A-Z]?)"

    match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)

    if match:
        content = match.group(1).strip()
        print("DEBUG: extract_swift_field match FOUND")
        return content

    print("DEBUG: extract_swift_field regex match NOT FOUND. Trying fallback...")

    # Fallback: check if starts with '46A' or ':46A:' or try .find
    start_index = full_text.find("46A")

    if start_index != -1:
        print(f"DEBUG: extract_swift_field fallback FOUND at index {start_index}")
        # Extract from the found index onwards
        content = full_text[start_index:]
        # Remove the tag itself validly
        # Identify if it was :46A: or 46A
        if content.startswith(":46A:"):
            content = content[5:].strip()
        elif content.startswith("46A:"):
            content = content[4:].strip()
        elif content.startswith("46A"):
            content = content[3:].strip()

        return content

    print("DEBUG: extract_swift_field match NOT FOUND")
    start_index = full_text.find("DOCUMENTS REQUIRED")
    if start_index != -1:
        print(f"DEBUG: extract_swift_field fallback FOUND at index {start_index}")
        content = full_text[start_index:]
        return content
    return None


def call_gemma(header, prompt):
    if settings.DEMO == 1:
        if not prompt:
            return ""
        response = client.chat.completions.create(
            model=settings.TYPHOON_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        You are a SWIFT LC (MT700) field extraction engine.
        Extract ONLY field 46A (DOCUMENTS REQUIRED).
        Return only conditions
        FIND CONTENT THAT ABOUT {header}
        Rules:
        - Extract ONLY documents under field 46A
        - Preserve original wording exactly
        - Do NOT summarize
        - Do NOT explain
                        """,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=8192,
        )
        return response.choices[0].message.content
    else:
        response = ollama.chat(
            model="qwen2.5:7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                You are a SWIFT LC (MT700) field extraction engine.
Extract ONLY field 46A (DOCUMENTS REQUIRED).

Return only conditions
FIND CONTENT THAT ABOUT {header}

Rules:
- Extract ONLY documents under field 46A
- Preserve original wording exactly
- Do NOT summarize
- Do NOT explain
                """,
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0},
        )
    content = response["message"]["content"]
    return content


def call_gemma_annexure(prompt):
    if settings.DEMO == 1:
        if not prompt:
            return ""
        response = client.chat.completions.create(
            model=settings.TYPHOON_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are a SWIFT LC (MT700) field extraction engine.
        Extract ONLY field 46A (DOCUMENTS REQUIRED).
        From field 46A, find **all content that mentions annexures in the INSPECTION_CERTIFICATE**.
        Return JSON with every annexure. Use the following format:
        "annexures": [
        { "code": "A", "text": "..." },
        { "code": "B", "text": "..." },
        { "code": "C", "text": "..." }
        ]
        Rules:
        - Extract ONLY documents under field 46A.
        - Preserve original wording exactly.
        - Do NOT summarize.
        - Do NOT explain.
        - Return valid JSON only.
        - Include **all annexures mentioned**, not only code A.
        """,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=8192,
        )
        content = response.choices[0].message.content
        # Try to extract JSON from markdown if present
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            # Try to find the first '{' and last '}'
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start : end + 1]
        return content
    else:
        response = ollama.chat(
            model="qwen2.5:7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """
                You are a SWIFT LC (MT700) field extraction engine.

Extract ONLY field 46A (DOCUMENTS REQUIRED).

From field 46A, find **all content that mentions annexures in the INSPECTION_CERTIFICATE**.

Return JSON with every annexure. Use the following format:

"annexures": [
{ "code": "A", "text": "..." },
{ "code": "B", "text": "..." },
{ "code": "C", "text": "..." }
]

Rules:
- Extract ONLY documents under field 46A.
- Preserve original wording exactly.
- Do NOT summarize.
- Do NOT explain.
- Return valid JSON only.
- Include **all annexures mentioned**, not only code A.
""",
                },
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0},
        )
    content = response["message"]["content"]

    # Try to extract JSON from markdown if present
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    else:
        # Try to find the first '{' and last '}'
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            content = content[start : end + 1]

    return content


def extract_document_require_46A(full_text: str):
    print("DEBUG: Inside extract_document_require_46A")
    items = []
    text = extract_swift_field(full_text)
    if not text:
        print("DEBUG: Field 46A not found")
        return {"items": []}
    print(f"DEBUG: extract_swift_field result: {text[:100] if text else 'None'}")
    print("46A : ", text)
    items.append(
        {"item_no": 1, "doc_type": "INVOICE", "conditions": call_gemma("INVOICE", text)}
    )
    items.append(
        {
            "item_no": 2,
            "doc_type": "BILL_OF_LADING",
            "conditions": call_gemma("BILL_OF_LADING", text),
        }
    )
    items.append(
        {
            "item_no": 3,
            "doc_type": "INSURANCE",
            "conditions": call_gemma("INSURANCE", text),
        }
    )

    # Handle optional annexures extraction
    annexures = []
    annexure_raw = call_gemma_annexure(text)
    try:
        if annexure_raw:
            annexure_json = json.loads(annexure_raw)
            annexures = annexure_json.get("annexures", [])
    except Exception as e:
        print(f"Error parsing annexures JSON: {e}")
        print(f"Raw response: {annexure_raw}")

    items.append(
        {
            "item_no": 4,
            "doc_type": "CERTIFICATE_OF_REGISTRATION",
            "conditions": call_gemma("CERTIFICATE_OF_REGISTRATION", text),
            "annexures": annexures,
        }
    )
    items.append(
        {
            "item_no": 5,
            "doc_type": "TRANSLATION",
            "conditions": call_gemma("TRANSLATION", text),
        }
    )
    items.append(
        {
            "item_no": 6,
            "doc_type": "INSPECTION_CERTIFICATE",
            "conditions": call_gemma("INSPECTION_CERTIFICATE", text),
        }
    )
    items.append(
        {
            "item_no": 7,
            "doc_type": "BENEFICIARY_CERTIFICATE",
            "conditions": call_gemma("BENEFICIARY_CERTIFICATE", text),
        }
    )
    return {"items": items}


def detect_amendment(full_text: str):
    amendment_keywords = [
        "AMENDMENT",
        "NUMBER OF AMENDMENT",
        ":26E",
        "DATE OF AMENDMENT",
        "THIS AMENDMENT",
    ]

    text_upper = full_text.upper()

    for k in amendment_keywords:
        if k in text_upper:
            return True

    return False


def extract_lc_by_ai(full_text):
    if settings.DEMO == 1:
        response = client.chat.completions.create(
            model=settings.TYPHOON_CHAT_MODEL,
            temperature=0,
            max_tokens=8192,
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert in SWIFT MT700 / MT707 LC documents.

Extract all LC fields.

If this is an AMENDMENT LC, return the UPDATED values.

Return JSON only.
""",
                },
                {
                    "role": "user",
                    "content": f"""
Extract LC information from this text.

Return JSON format:

{{
"lc_no": "",
"beneficiary_59": "",
"applicant_50": "",
"date_of_issue_31c": "",
"date_of_amendment_30": "",
"number_of_amendment_26e": "",
"description_of_goods_45a": [
    {{ "item_no": 1, "description": "" }}
],
"documents_required_46a": {{ "items": [] }},
"sequence_of_total_27": "",
"sender_reference_20": "",
"receiver_reference_21": "",
"issuing_bank_reference_23": "",
"issuing_bank_52a": "",
"purpose_of_message_22a": "",
"applicable_rules_40e": "",
"latest_date_of_shipment_44c": "",
"additional_conditions_47a": "",
"additional_conditions_47b": "",
"currency_code_32b": "",
"date_and_place_of_expiry_31d": "",
"form_of_documentary_credit_40a": "",
"available_with_41d": "",
"partial_shipments_43p": "",
"transhipment_43t": "",
"port_of_discharge_44f": "",
"port_of_loading_of_departure_44e": "",
"charges_71d": "",
"period_for_presentation_in_days_48": "",
"confirmation_instructions_49": "",
"instructions_to_the_paying_accepting_negotiating_bank_78": "",
"applicant_bank_51d": "",
"drafts_at_42c": "",
"drawee_42a": ""
}}

TEXT:
{full_text}
""",
                },
            ],
        )

        content = response.choices[0].message.content

        # Try to extract JSON from markdown if present
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            # Try to find the first '{' and last '}'
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                content = content[start : end + 1]

        try:
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing AI extraction JSON: {e}")
            return {}
    else:
        import ollama

        response = ollama.chat(
            model="qwen2.5:7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an expert in SWIFT MT700 / MT707 LC documents.

Extract all LC fields.

If this is an AMENDMENT LC, return the UPDATED values.

Return JSON only.
""",
                },
                {
                    "role": "user",
                    "content": f"""
Extract LC information from this text.

Return JSON format:

{{
"lc_no": "",
"beneficiary_59": "",
"applicant_50": "",
"date_of_issue_31c": "",
"date_of_amendment_30": "",
"number_of_amendment_26e": "",
"description_of_goods_45a": [
    {{ "item_no": 1, "description": "" }}
],
"documents_required_46a": {{ "items": [] }},
"sequence_of_total_27": "",
"sender_reference_20": "",
"receiver_reference_21": "",
"issuing_bank_reference_23": "",
"issuing_bank_52a": "",
"purpose_of_message_22a": "",
"applicable_rules_40e": "",
"latest_date_of_shipment_44c": "",
"additional_conditions_47a": "",
"additional_conditions_47b": "",
"currency_code_32b": "",
"date_and_place_of_expiry_31d": "",
"form_of_documentary_credit_40a": "",
"available_with_41d": "",
"partial_shipments_43p": "",
"transhipment_43t": "",
"port_of_discharge_44f": "",
"port_of_loading_of_departure_44e": "",
"charges_71d": "",
"period_for_presentation_in_days_48": "",
"confirmation_instructions_49": "",
"instructions_to_the_paying_accepting_negotiating_bank_78": "",
"applicant_bank_51d": "",
"drafts_at_42c": "",
"drawee_42a": ""
}}

TEXT:
{full_text}
""",
                },
            ],
            options={"temperature": 0},
            format="json",
        )
        content = response["message"]["content"]
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing Ollama extraction JSON: {e}")
            return {}
