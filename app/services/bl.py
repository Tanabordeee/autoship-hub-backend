from sqlalchemy.orm import Session
import re
from app.services.ocr_service import extract_text_from_path
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.repositories.lc_repo import LCRepo
from app.repositories.booking import BookingRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.si import SI_Repository
from datetime import datetime
from app.repositories.bl import BLRepository
from app.schemas.bl import BLCreate
from app.services.audit_log_service import audit_log_service
from app.core.config import settings
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobUpdate
import logging
from app.db.session import SessionLocal
from .bl_parser import extract_bl_by_ai

logger = logging.getLogger(__name__)


def extract_bl(db: Session, file_path: str, transaction_id: int, user_id: int):
    try:
        text = extract_text_from_path(file_path)

        # Call AI Typhoon for extraction
        ai_data = extract_bl_by_ai(text)

        # Ensure we have a valid data dictionary
        data = {
            "bl_number": ai_data.get("bl_number"),
            "jo_number": ai_data.get("jo_number"),
            "ocean_vessel": ai_data.get("ocean_vessel"),
            "port_of_loading": ai_data.get("port_of_loading"),
            "port_of_discharge": ai_data.get("port_of_discharge"),
            "freight_payable_at": ai_data.get("freight_payable_at"),
            "number_of_original_bs": ai_data.get("number_of_original_bs"),
            "gross_weight": ai_data.get("gross_weight"),
            "measurement": ai_data.get("measurement"),
            "shipper": ai_data.get("shipper"),
            "consignee": ai_data.get("consignee"),
            "notify_party": ai_data.get("notify_party"),
            "cy_cf": ai_data.get("cy_cf"),
            "description_of_good": ai_data.get("description_of_good"),
            "container": ai_data.get("container"),
            "seal_no": ai_data.get("seal_no"),
            "size_no": ai_data.get("size_no"),
            "place_of_receipt": ai_data.get("place_of_receipt"),
            "place_of_delivery": ai_data.get("place_of_delivery"),
            "text": text,
        }

        # Update transaction status
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="pending", current_process="bl"),
            user_id=user_id,
        )

        # Log action
        audit_log_service.log_action(db, "extract", "bl", user_id, transaction_id)

        return data
    except Exception as e:
        logger.error(f"Error extracting BL: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting BL: {str(e)}")
        raise


def process_bl_extraction(
    job_id: str, file_path: str, user_id: int, transaction_id: int
):
    db = SessionLocal()
    try:
        ExtractionJobRepo.update(db, job_id, ExtractionJobUpdate(status="processing"))
        result = extract_bl(db, file_path, transaction_id, user_id)
        ExtractionJobRepo.update(
            db, job_id, ExtractionJobUpdate(status="completed", result=result)
        )
    except Exception as e:
        ExtractionJobRepo.update(
            db, job_id, ExtractionJobUpdate(status="failed", error_message=str(e))
        )
    finally:
        db.close()


def confirm_bl(db: Session, transaction_id: int, bl_id: int, user_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="confirm", current_process="bl", bl_id=bl_id),
            user_id=user_id,
        )
        audit_log_service.log_action(db, "confirm", "bl", user_id, transaction_id)
        return True
    except Exception as e:
        print(e)
    return False


def reject_bl(db: Session, transaction_id: int, bl_id: int, user_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="reject", current_process="bl", bl_id=bl_id),
            user_id=user_id,
        )
        audit_log_service.log_action(db, "reject", "bl", user_id, transaction_id)
        return True
    except Exception as e:
        print(e)
        return False


def get_check_data(db: Session, payload):
    lc = LCRepo.get_by_id(db, payload.lc_id)
    booking = BookingRepo.get_by_id(db, payload.booking_id)
    vehicle_register = VehicleRegisterRepo.get_by_id(db, payload.vehicle_register_id)
    proforma_invoice = ProformaInvoiceRepo.get_by_id(db, payload.pi_id)
    si = SI_Repository.get_by_id(db, payload.si_id)
    item_first_text = lc.document_require_46a["items"][0]["conditions"]
    match = re.search(
        r"(?:AS\s*)?PER\s*PROFORMA\s*INVOICE\s*NO\.?\s*[A-Z0-9-]+\s*OF\s*\d{1,2}\.\d{1,2}\.\d{4}",
        item_first_text,
    )
    as_per_proforma_invoice = match.group(0) if match else ""
    date_str = booking.etd
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    etd = dt.strftime("%B %d, %Y").upper()
    return {
        "lc": lc,
        "booking": booking,
        "vehicle_register": vehicle_register,
        "proforma_invoice": proforma_invoice,
        "si": si,
        "as_per_proforma_invoice": as_per_proforma_invoice,
        "etd": etd,
        "number_of_original_bs": si.number_of_original_bs,
    }


def create_bl(db: Session, payload: BLCreate):
    existing_bl = BLRepository.get_latest_version_by_bl_no(db, payload.bl_number)
    if existing_bl:
        # Increment version
        new_version = (existing_bl.version_bl or 0) + 1

        # Merge None fields from new payload with existing LC data
        payload_dict = payload.model_dump()

        for field, value in payload_dict.items():
            if value is None and hasattr(existing_bl, field):
                # If new value is None, use the old value
                old_value = getattr(existing_bl, field)
                setattr(payload, field, old_value)

        # Set the new version number
        payload.version_bl = new_version
    else:
        # First version
        payload.version_bl = 1
    bl = BLRepository.create(db, payload)
    ProformaInvoiceRepo.update_bl_pi_items(db, payload.chassis, bl.id)
    return bl


def get_bl_by_id(db: Session, id: int):
    return BLRepository.get_all_versions_by_id(db, id)
