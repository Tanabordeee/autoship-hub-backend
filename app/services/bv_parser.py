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


def extract_bv_by_ai(full_text):
    prompt = f"""
Extract Bureau Veritas (BV) / Inspection Certificate information from this text.

Return JSON format with the following fields:

{{
"type_of_vehicle": "",
"make": "",
"model": "",
"seat": "",
"commonly_called": "",
"manufacture_grade": "",
"body_colour": "",
"fuel_type": "",
"year_of_manufacture": "",
"inspection_mileage": "",
"engine_capacity": "",
"engine_no": "",
"driving_system": "",
"marks_of_accident_on_chassis": "",
"chassis_no":"",
"condition_of_chassis": "",
"country_of_origin": "",
"year_month_of_first_registration": "",
"code_no": "",
"date": "",
"bv_ref_no": "",
"lc_no": ""
}}

Rules:
- If a field is not found, return null.
- For "inspection_mileage", include the unit (e.g., "50,000 KM").
- For "engine_capacity", include the unit (e.g., "2500 CC").
- "date" should be the certificate date (e.g., "January 14, 2026").
- "year_month_of_first_registration" should be in YYYY/MM/DD format if possible.
- Return ONLY the JSON object.

TEXT:
{full_text}
"""

    if settings.DEMO == 1:
        response = client.chat.completions.create(
            model=settings.TYPHOON_CHAT_MODEL,
            temperature=0,
            max_tokens=8192,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in vehicle inspection certificates and BV document extraction. Return JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
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
            print(f"Error parsing BV AI extraction JSON: {e}")
            return {}
    else:
        import ollama

        response = ollama.chat(
            model="qwen2.5:7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in vehicle inspection certificates and BV document extraction. Return JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={"temperature": 0},
            format="json",
        )
        content = response["message"]["content"]
        try:
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing BV Ollama extraction JSON: {e}")
            return {}
