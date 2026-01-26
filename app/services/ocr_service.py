import base64
import requests
import io
from app.core.config import settings
from PIL import Image
from pdf2image import convert_from_bytes
from fastapi import UploadFile


def ocr_image(image: Image.Image, model: str = None):
    """Helper function to OCR a single PIL Image using central settings"""
    if model is None:
        model = settings.OCR_MODEL

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


def extract_text_from_file(file: UploadFile, model: str = None):
    """
    Extract text from an uploaded file (PDF or Image).
    Converts PDF pages to images or opens an image file, then performs OCR.
    """
    content = file.file.read()
    filename = file.filename.lower()

    images = []

    if filename.endswith(".pdf"):
        # Convert PDF to images
        pages = convert_from_bytes(content, dpi=300, poppler_path=settings.POPPLER_PATH)
        images.extend(pages)
    else:
        # Assume it's an image
        try:
            image = Image.open(io.BytesIO(content)).convert("RGB")
            images.append(image)
        except Exception as e:
            print(f"Failed to open image: {e}")
            return f"[Error: Could not open file as image or PDF: {e}]"

    results = []
    for idx, img in enumerate(images):
        print(f"OCR processing page/image {idx + 1}/{len(images)}")
        text = ocr_image(img, model)
        results.append(text.strip())

    return "\n\n".join(results)
