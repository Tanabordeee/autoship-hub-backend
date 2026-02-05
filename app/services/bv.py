from sqlalchemy.orm import Session
from fastapi import UploadFile
from PyPDF2 import PdfReader, PdfWriter

import io
import numpy as np
from PIL import Image

from pdf2image import convert_from_bytes
import easyocr
import re
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.repositories.bv import BVRepository
from app.schemas.bv import BVCreate
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.repositories.lc_repo import LCRepo
import logging

logger = logging.getLogger(__name__)
# =========================
# EasyOCR (init ครั้งเดียว)
# =========================
reader = easyocr.Reader(
    ["en"],  # เพิ่ม 'th' ได้ถ้าต้องการ
    gpu=False,
)


# =========================
# OCR image ด้วย EasyOCR
# =========================
def ocr_image(img: Image.Image) -> str:
    img_np = np.array(img)

    results = reader.readtext(img_np, detail=0, paragraph=True)

    return "\n".join(results)


# =========================
# Extract text from file
# (PDF / Image)
# =========================
def extract_text_from_file(file: UploadFile):
    content = file.file.read()
    filename = file.filename.lower()

    images = []

    if filename.endswith(".pdf"):
        pages = convert_from_bytes(
            content,
            dpi=300,
            # ถ้ามี poppler_path ใส่เพิ่มได้
            # poppler_path=settings.POPPLER_PATH
        )
        images.extend(pages)
    else:
        image = Image.open(io.BytesIO(content)).convert("RGB")
        images.append(image)

    results = []
    for img in images:
        text = ocr_image(img)
        results.append(text.strip())

    return "\n\n".join(results)


def extract(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else None


def clean_ocr_text(text: str) -> str:
    # normalize newline
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # remove weird OCR artifacts
    text = re.sub(r"[|{}[\]]", " ", text)

    # fix common OCR mistakes (BV specific)
    replacements = {
        "Modcl": "Model",
        "manufacturc": "manufacture",
        "Aulomatic": "Automatic",
        "UREAU": "BUREAU",
        "B UREAU": "BUREAU",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # trim garbage tail (optional but helps a lot)
    text = re.split(r"Inirenti n|ORIGINAL", text)[0]

    return text.strip()


# =========================
# Extract BV (หน้าแรกเท่านั้น)
# =========================
def extract_bv(db: Session, file: UploadFile, transaction_id: int):
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        writer = PdfWriter()

        # เอาเฉพาะหน้าแรก
        writer.add_page(reader.pages[0])

        pdf_bytes = io.BytesIO()
        writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        file = UploadFile(filename=file.filename, file=pdf_bytes)

    text = extract_text_from_file(file)
    text = clean_ocr_text(text)
    type_of_vehicle = r"Type\s*of\s*vehicle\s+([A-Za-z0-9\s\(\)\-\/]+)"
    make = r"Make\s+([A-Za-z0-9\s\-]+)"
    model = r"Model\s+([A-Za-z0-9\.,\sL]+)"
    seat = r"(?:Seat|Seai)\s+(\d+\s*Seats?)"
    commonly_called = r"Commonly\s+called\s+([A-Za-z0-9\s\-]+)"
    manufacture_grade = r"Manufacture\s+Grade.*?\s([A-Z])"
    body_colour = r"Body\s+colou?r\s+([A-Za-z]+)"
    fuel_type = r"Fuel\s+type\s+([A-Za-z]+)"
    year_of_manufacture = r"Year\s+of\s+manufacture\s+(\d{4})"
    year_month_of_first_registration = (
        r"Year.*?first\s+registration\s+(\d{4}\/\d{2}\/\d{2})"
    )
    inspection_mileage = r"Inspection\s+mileage.*?\s([\d,\.]+\s*KM)"
    engine_capacity = r"Engine\s+capac\w*\s+(\d+\s*CC)"
    engine_no = r"Engine\s+No\.?\s+([A-Z0-9]+)"
    driving_system = r"Driving\s+system\s+([A-Za-z]+)"
    marks_of_accident_on_chassis = (
        r"Marks\s+of\s+accident\s+on\s+chassis.*?:\s*(.*?)(?:\d{1,2}[,\.]|\n)"
    )
    condition_of_chassis = r"Condition\s+o[f|l]\s+chassis\s+([A-Za-z]+)"
    country_of_origin = r"Country\s+of\s+Origin\s+([A-Za-z]+)"
    code_no = r"CODE\s+No\s+(\d+)"
    date = r"DATE\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})"
    bv_ref_no = r"BV\s+Ref\s+No:\s*([A-Z0-9\-()]+)"
    lc_no = r"LC\s+No\.?:\s*(\d+)"
    data = {
        "type_of_vehicle": extract(type_of_vehicle, text),
        "make": extract(make, text),
        "model": extract(model, text),
        "seat": extract(seat, text),
        "commonly_called": extract(commonly_called, text),
        "manufacture_grade": extract(manufacture_grade, text),
        "body_colour": extract(body_colour, text),
        "fuel_type": extract(fuel_type, text),
        "year_of_manufacture": extract(year_of_manufacture, text),
        "inspection_mileage": extract(inspection_mileage, text),
        "engine_capacity": extract(engine_capacity, text),
        "engine_no": extract(engine_no, text),
        "driving_system": extract(driving_system, text),
        "marks_of_accident_on_chassis": extract(marks_of_accident_on_chassis, text),
        "condition_of_chassis": extract(condition_of_chassis, text),
        "country_of_origin": extract(country_of_origin, text),
        "year_month_of_first_registration": extract(
            year_month_of_first_registration, text
        ),
        "code_no": extract(code_no, text),
        "date": extract(date, text),
        "bv_ref_no": extract(bv_ref_no, text),
        "lc_no": extract(lc_no, text),
    }
    # ---------- CHECK OTHER PAGES ----------
    bv_mismatch_pages = []
    bv_ref_pattern = r"BV\s*(?:Ref\s*)?No\s*[:]{1,2}\s*([A-Z0-9\-()]+)"
    for i in range(1, len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        page_bytes = io.BytesIO()
        writer.write(page_bytes)
        page_bytes.seek(0)

        page_file = UploadFile(filename=file.filename, file=page_bytes)
        page_text = clean_ocr_text(extract_text_from_file(page_file))

        bv_ref_page = extract(bv_ref_pattern, page_text)
        bv_mismatch_pages.append(
            {
                "page": i + 1,
                "found": bv_ref_page,
                "expected": data["bv_ref_no"],
            }
        )
    if bv_mismatch_pages:
        data["bv_mismatch_pages"] = bv_mismatch_pages
    TransactionRepo.update(
        db,
        int(transaction_id),
        TransactionUpdate(status="pending", current_process="bv"),
    )
    return data


def create_bv(db: Session, payload: BVCreate):
    payload.bv_ref_no = payload.bv_ref_no.strip()
    existing_bv = BVRepository.get_latest_version_by_bv_ref_no(db, payload.bv_ref_no)
    if existing_bv:
        logger.info(f"Existing BV found for {payload.bv_ref_no}")
        # Increment version
        new_version = (existing_bv.version_bv or 0) + 1

        # Merge None fields from new payload with existing LC data
        payload_dict = payload.model_dump()

        for field, value in payload_dict.items():
            if value is None and hasattr(existing_bv, field):
                # If new value is None, use the old value
                old_value = getattr(existing_bv, field)
                setattr(payload, field, old_value)

        # Set the new version number
        payload.version_bv = new_version
    else:
        # First version
        payload.version_bv = 1
    logger.info(f"Creating BV with version {payload.version_bv}")
    bv = BVRepository.create(db, payload)
    ProformaInvoiceRepo.update_bv_pi_items(db, payload.chassis, bv.id)
    return bv


def confirm_bv(db: Session, transaction_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="confirm", current_process="bv"),
        )
    except Exception as e:
        print(e)
    return True


def reject_bv(db: Session, transaction_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="reject", current_process="bv"),
        )
    except Exception as e:
        print(e)
    return True


def get_check_bv(db: Session, chassis: str):
    vr = VehicleRegisterRepo.get_by_chassis(db, chassis)
    logger.info(f"Vehicle Register found for {vr}")
    logger.info(f"{chassis}")
    lc_no = LCRepo.get_all_lc_no(db)
    return {
        "chassis": vr.chassis_no if vr else None,
        "make": vr.vehicle_make if vr else None,
        "model": vr.model if vr else None,
        "seat": vr.seat if vr else None,
        "colour": vr.colour if vr else None,
        "fuel_type": vr.fuel_type if vr else None,
        "engine_no": vr.engine_no if vr else None,
        "model_year": vr.model_year if vr else None,
        "date_of_registration": vr.date_of_registration if vr else None,
        "lc_no": lc_no,
    }
