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


def extract_bl_by_ai(full_text):
    prompt = f"""
Extract Bill of Lading (BL) information from this text.

Return JSON format with the following fields:

{{
"bl_number": "",
"jo_number": "",
"ocean_vessel": "",
"port_of_loading": "",
"port_of_discharge": "",
"freight_payable_at": "",
"number_of_original_bs": "",
"gross_weight": "",
"measurement": "",
"shipper": "",
"consignee": "",
"notify_party": "",
"cy_cf": "",
"description_of_good": "",
"container": "",
"seal_no": "",
"size_no": "",
"place_of_receipt": "",
"place_of_delivery": ""
}}

Rules:
- If a field is not found, return null.
- For "gross_weight", include the unit (e.g., "15,000.00 KGS").
- For "measurement", include the unit (e.g., "30.000 CBM").
- Extract the full block of text for shipper, consignee, and notify_party.
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
                    "content": "You are an expert in shipping documents and Bill of Lading extraction. Return JSON only.",
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
            print(f"Error parsing BL AI extraction JSON: {e}")
            return {}
    else:
        import ollama

        response = ollama.chat(
            model="qwen2.5:7b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in shipping documents and Bill of Lading extraction. Return JSON only.",
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
            print(f"Error parsing BL Ollama extraction JSON: {e}")
            return {}
