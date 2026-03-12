from sqlalchemy.orm import Session
from fastapi import UploadFile
from PyPDF2 import PdfReader, PdfWriter

import io
from PIL import Image
from pdf2image import convert_from_bytes
import re
from app.core.config import settings
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.repositories.bv import BVRepository
from app.schemas.bv import BVCreate
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.repositories.lc_repo import LCRepo
import logging
from app.services.audit_log_service import audit_log_service
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate, ExtractionJobUpdate
import os
import uuid
from app.db.session import SessionLocal

from .bv_parser import extract_bv_by_ai
from app.services.ocr_service import (
    extract_text_from_path as ocr_extract_text,
    extract_text_from_bytes,
)

logger = logging.getLogger(__name__)

# EasyOCR reader is no longer needed since we use AI/Typhoon OCR


# OCR functions are no longer needed


# =========================
# Extract text from file
# (PDF / Image)
# =========================
def extract_text_from_file(file: UploadFile):
    content = file.file.read()
    filename = file.filename.lower()
    return _extract_text_from_bytes(content, filename)


def extract_text_from_path(file_path: str):
    with open(file_path, "rb") as f:
        content = f.read()
    filename = os.path.basename(file_path).lower()
    return _extract_text_from_bytes(content, filename)


def _extract_text_from_bytes(content: bytes, filename: str):
    # This is a fallback for non-demo mode or local OCR if needed
    images = []

    if filename.endswith(".pdf"):
        pages = convert_from_bytes(
            content,
            dpi=300,
        )
        images.extend(pages)
    else:
        try:
            image = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception:
            return ""

    # Note: Using Typhoon OCR as primary via extract_text_from_bytes
    return extract_text_from_bytes(content, filename)


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


def extract_bv(
    db: Session, file_path: str, transaction_id: int, user_id: int, job_id: str = None
):
    try:
        filename = file_path.lower()

        if filename.endswith(".pdf"):
            with open(file_path, "rb") as f:
                reader_pdf = PdfReader(f)
                # We need the first page for main extraction
                writer = PdfWriter()
                writer.add_page(reader_pdf.pages[0])
                pdf_bytes = io.BytesIO()
                writer.write(pdf_bytes)
                pdf_bytes.seek(0)
                content = pdf_bytes.read()
                
                # Use Typhoon OCR if in DEMO mode
                if settings.DEMO == 1:
                    first_page_text = extract_text_from_bytes(content, filename)
                else:
                    first_page_text = _extract_text_from_bytes(content, filename)
        else:
            first_page_text = ocr_extract_text(file_path)

        # Call AI Typhoon for main extraction from the first page
        ai_data = extract_bv_by_ai(first_page_text)
        
        data = {
            "type_of_vehicle": ai_data.get("type_of_vehicle"),
            "make": ai_data.get("make"),
            "model": ai_data.get("model"),
            "seat": ai_data.get("seat"),
            "commonly_called": ai_data.get("commonly_called"),
            "manufacture_grade": ai_data.get("manufacture_grade"),
            "body_colour": ai_data.get("body_colour"),
            "fuel_type": ai_data.get("fuel_type"),
            "year_of_manufacture": ai_data.get("year_of_manufacture"),
            "inspection_mileage": ai_data.get("inspection_mileage"),
            "engine_capacity": ai_data.get("engine_capacity"),
            "engine_no": ai_data.get("engine_no"),
            "driving_system": ai_data.get("driving_system"),
            "marks_of_accident_on_chassis": ai_data.get("marks_of_accident_on_chassis"),
            "condition_of_chassis": ai_data.get("condition_of_chassis"),
            "country_of_origin": ai_data.get("country_of_origin"),
            "year_month_of_first_registration": ai_data.get("year_month_of_first_registration"),
            "code_no": ai_data.get("code_no"),
            "date": ai_data.get("date"),
            "bv_ref_no": ai_data.get("bv_ref_no"),
            "lc_no": ai_data.get("lc_no"),
        }

        # ---------- CHECK OTHER PAGES FOR MATCHING BV REF ----------
        bv_mismatch_pages = []
        if filename.endswith(".pdf"):
            with open(file_path, "rb") as f:
                reader_pag = PdfReader(f)
                for i in range(1, len(reader_pag.pages)):
                    writer = PdfWriter()
                    writer.add_page(reader_pag.pages[i])
                    page_bytes = io.BytesIO()
                    writer.write(page_bytes)
                    page_bytes.seek(0)
                    page_content = page_bytes.read()
                    
                    if settings.DEMO == 1:
                        page_text = extract_text_from_bytes(page_content, filename)
                    else:
                        page_text = _extract_text_from_bytes(page_content, filename)
                    
                    # Still use regex for quick reference check on other pages
                    bv_ref_pattern = r"BV\s*(?:Ref\s*)?No\s*[:]{1,2}\s*([A-Z0-9\-()]+)"
                    bv_ref_page = extract(bv_ref_pattern, page_text)
                    
                    if bv_ref_page != data["bv_ref_no"]:
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
            user_id=user_id,
        )
        audit_log_service.log_action(db, "extract", "bv", user_id, transaction_id)
        return data
    except Exception as e:
        logger.error(f"Error extracting BV: {str(e)}")
        raise


def process_bv_extraction(
    job_id: str, file_path: str, user_id: int, transaction_id: int
):
    db = SessionLocal()
    try:
        ExtractionJobRepo.update(db, job_id, ExtractionJobUpdate(status="processing"))
        result = extract_bv(db, file_path, transaction_id, user_id, job_id)
        ExtractionJobRepo.update(
            db, job_id, ExtractionJobUpdate(status="completed", result=result)
        )
    except Exception as e:
        ExtractionJobRepo.update(
            db, job_id, ExtractionJobUpdate(status="failed", error_message=str(e))
        )
    finally:
        db.close()


def create_bv(db: Session, payload: BVCreate, transaction_id: int, user_id: int):
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
    TransactionRepo.update(
        db,
        transaction_id,
        TransactionUpdate(status="completed", current_process="bv", bv_id=bv.id),
        user_id=user_id,
    )
    return bv


def confirm_bv(db: Session, transaction_id: int, user_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="confirm", current_process="bv"),
            user_id=user_id,
        )
        audit_log_service.log_action(db, "confirm", "bv", user_id, transaction_id)
        return True
    except Exception as e:
        print(e)
    return False


def reject_bv(db: Session, transaction_id: int, user_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="reject", current_process="bv"),
            user_id=user_id,
        )
        audit_log_service.log_action(db, "reject", "bv", user_id, transaction_id)
        return True
    except Exception as e:
        print(e)
    return False


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


def get_bv_by_id(db: Session, id: int):
    return BVRepository.get_all_versions_by_id(db, id)
