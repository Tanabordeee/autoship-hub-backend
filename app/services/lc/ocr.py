import base64
import requests
import io


def ocr_image(image, model: str):
    """Helper function to OCR a single image"""
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    img_base64 = base64.b64encode(buf.getvalue()).decode()

    payload = {
        "model": model,
        "prompt": "อ่านข้อความทั้งหมดในภาพนี้อย่างละเอียด\n- รักษาลำดับบรรทัด\n- ไม่สรุป\n- ไม่ตีความ\n- พิมพ์ตามต้นฉบับ 100%",
        "images": [img_base64],
        "stream": False,
    }

    r = requests.post("http://localhost:11434/api/generate", json=payload)

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
