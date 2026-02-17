from fastapi import UploadFile
import easyocr
import numpy as np
from pdf2image import convert_from_bytes
from PIL import Image
import io
import json

# Initialize EasyOCR reader
reader = easyocr.Reader(["en"], gpu=False)  # CPU only


def is_pdf(file_bytes):
    """Check if file is a PDF"""
    return file_bytes.startswith(b"%PDF")


def is_image(file_bytes):
    """Check if file is an image (JPEG, PNG, etc.)"""
    # JPEG signatures
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return True
    # PNG signature
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # GIF signature
    if file_bytes.startswith(b"GIF87a") or file_bytes.startswith(b"GIF89a"):
        return True
    # BMP signature
    if file_bytes.startswith(b"BM"):
        return True
    # WebP signature
    if file_bytes[0:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return True
    return False


async def boundingbox(upload_file: UploadFile):
    # อ่านไฟล์เป็น bytes
    file_bytes = await upload_file.read()

    # Validate that we received data
    if not file_bytes:
        raise ValueError("Uploaded file is empty")

    pages = []

    # ตรวจสอบประเภทไฟล์และประมวลผลตามประเภท
    if is_pdf(file_bytes):
        # แปลง PDF เป็น list ของ images
        try:
            pages = convert_from_bytes(file_bytes, dpi=300)
        except Exception as e:
            raise ValueError(
                f"Failed to process PDF file: {str(e)}. The file may be corrupted or invalid."
            )
    elif is_image(file_bytes):
        # เปิดไฟล์รูปภาพโดยตรง
        try:
            image = Image.open(io.BytesIO(file_bytes))
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if image.mode != "RGB":
                image = image.convert("RGB")

            # ลดขนาดรูปภาพถ้าใหญ่เกินไป เพื่อป้องกันปัญหา memory
            max_dimension = 3000  # ขนาดสูงสุดที่ยอมรับได้
            width, height = image.size
            if width > max_dimension or height > max_dimension:
                # คำนวณ scale ratio
                ratio = min(max_dimension / width, max_dimension / height)
                new_size = (int(width * ratio), int(height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(
                    f"Resized image from {width}x{height} to {new_size[0]}x{new_size[1]}"
                )

            pages = [image]
        except Exception as e:
            raise ValueError(
                f"Failed to process image file: {str(e)}. The file may be corrupted or invalid."
            )
    else:
        raise ValueError(
            f"Unsupported file type. Please upload a PDF or image file (JPEG, PNG, GIF, BMP, WebP). "
            f"File starts with: {file_bytes[:20]}"
        )
    all_pages = []

    for page_index, page in enumerate(pages):
        print(f"Processing Page {page_index + 1}")
        img_array = np.array(page)

        # OCR with EasyOCR
        results = reader.readtext(img_array)
        # results = [(bbox, text, confidence), ...]

        w_img, h_img = page.size
        page_boxes = []

        for bbox, text, confidence in results:
            # bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]

            x = min(x_coords)
            y = min(y_coords)
            width = max(x_coords) - x
            height = max(y_coords) - y

            page_boxes.append(
                {
                    "text": text,
                    "confidence": float(confidence),
                    "x": x / w_img,
                    "y": y / h_img,
                    "width": width / w_img,
                    "height": height / h_img,
                }
            )

        all_pages.append(
            {
                "page": page_index + 1,
                "page_width": w_img,
                "page_height": h_img,
                "boxes": page_boxes,
            }
        )

    # Save JSON
    with open("ocr_easyocr.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, indent=2, ensure_ascii=False)

    print("Done. Results saved to ocr_easyocr.json")
    return all_pages
