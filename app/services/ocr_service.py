import json
import io
import requests
from app.core.config import settings
from PIL import Image
from pdf2image import convert_from_bytes
from fastapi import UploadFile
import base64


def ocr_image(image: Image.Image, model: str = "typhoon-ocr"):
    if settings.DEMO == 1:
        """Helper function to OCR a single PIL Image using Typhoon OCR API"""
        url = settings.TYPHOON_OCR_URL
        api_key = settings.TYPHOON_API_KEY

        # Convert PIL Image to bytes
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        files = {"file": ("image.png", buf, "image/png")}
        data = {
            "model": model,
            "task_type": "default",
            "max_tokens": "16384",
            "temperature": "0.1",
            "top_p": "0.6",
            "repetition_penalty": "1.2",
        }

        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            r = requests.post(url, files=files, data=data, headers=headers)
            if r.status_code == 200:
                result = r.json()
                extracted_texts = []
                for page_result in result.get("results", []):
                    if page_result.get("success") and page_result.get("message"):
                        content = page_result["message"]["choices"][0]["message"][
                            "content"
                        ]
                        try:
                            # Try to parse as JSON if it's structured output
                            parsed_content = json.loads(content)
                            text = parsed_content.get("natural_text", content)
                        except json.JSONDecodeError:
                            text = content
                        extracted_texts.append(text)
                    elif not page_result.get("success"):
                        print(
                            f"Error processing {page_result.get('filename', 'unknown')}: {page_result.get('error', 'Unknown error')}"
                        )

                return "\n".join(extracted_texts) if extracted_texts else ""
            else:
                print(f"Typhoon API Error: {r.status_code} - {r.text}")
                return f"[Error: Typhoon API returned {r.status_code}]"
        except Exception as e:
            print(f"Exception during Typhoon OCR: {e}")
            return f"[Error: OCR failed: {e}]"
    else:
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
    filename = file.filename.lower()
    content = file.file.read()

    return extract_text_from_bytes(content, filename, model)


def extract_text_from_path(file_path: str, model: str = None):
    """
    Extract text from a local file path (PDF or Image).
    """
    filename = file_path.lower()
    with open(file_path, "rb") as f:
        content = f.read()

    return extract_text_from_bytes(content, filename, model)


def extract_text_from_bytes(content: bytes, filename: str, model: str = None):
    """
    Core logic to extract text from file bytes.
    """
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
