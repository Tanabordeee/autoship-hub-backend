from sqlalchemy.orm import Session
import re

# from app.repositories.transaction_repo import TransactionRepo
# from app.schemas.transaction import TransactionUpdate
from app.services.ocr_service import extract_text_from_file
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.repositories.lc_repo import LCRepo
from app.repositories.booking import BookingRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.si import SI_Repository
from datetime import datetime
import num2words


def extract_block(text, label):
    """
    ดึงข้อความใต้หัวข้อ จนกว่าจะเจอหัวข้อถัดไปหรือบรรทัดว่างใหญ่
    """
    pattern = rf"{label}\s*:\s*\n(.*?)(?=\n\n[A-Z/ ]+?:|\n\n[A-Z][A-Za-z ]+\n|$)"
    m = re.search(pattern, text, re.S | re.I)
    return m.group(1).strip() if m else None


def extract_single(text, pattern):
    m = re.search(pattern, text, re.I)
    return m.group(1).strip() if m else None


def extract_bl(db: Session, file, transaction_id: str):
    text = extract_text_from_file(file)
    data = {}
    data["bl_number"] = extract_single(text, r"B/L Number\s*\n([A-Z0-9]+)")
    data["jo_number"] = extract_single(text, r"J/O Number\s*\n([A-Z0-9]+)")
    data["ocean_vessel"] = extract_single(
        text, r"Ocean Vessel\s*\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )

    data["port_of_loading"] = extract_single(
        text, r"Port of Loading\s*\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )

    data["port_of_discharge"] = extract_single(
        text, r"Port of Discharge.*?\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )

    data["freight_payable_at"] = extract_single(
        text, r"Freight Payable at\s*\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )

    data["number_of_original_bl"] = extract_single(
        text, r"Number of Original Bs/L\s*\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )
    data["gross_weight"] = extract_single(text, r"(\d{1,3}(?:,\d{3})*\.\d+\s*KGS)")

    data["measurement"] = extract_single(text, r"(\d+\.\d+\s*CBM)")

    data["shipper"] = extract_block(text, "Shipper")
    data["consignee"] = extract_block(text, "Consignee")
    data["notify_party"] = extract_block(text, "Notify Party")
    data["cy_cf"] = extract_single(text, r"SHIPPED\s+ON\s+BOARD\s*:\s*([^</]+)")
    data["description_of_goods"] = extract_single(
        text, r"(SHIPPER'S\s+LOAD\s+COUNT[\s\S]*?)(?=\d{1,3},\d{3}\.?\d*\s*KGS)"
    )
    container_seal_size_match = re.search(
        r"([A-Z]{4}\d{7})\/(\d{6,})\/(\d{2}'HQ)", text
    )
    if container_seal_size_match:
        data["container"] = container_seal_size_match.group(1) or None
        data["seal_no"] = container_seal_size_match.group(2) or None
        data["size"] = container_seal_size_match.group(3) or None
    data["place_of_receipt"] = extract_single(
        text,
        r"Place of receipt\s*\n\s*([A-Z ,]+)(?:\/)?",
    )
    data["place_of_delivery"] = extract_single(
        text,
        r"Place of Delivery\s*\n\s*([A-Z ,]+)(?:\/)?",
    )
    TransactionRepo.update(
        db,
        int(transaction_id),
        TransactionUpdate(status="pending", current_process="bl"),
    )
    return data


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
        "as_per_proforma_invoice": as_per_proforma_invoice,
        "etd": etd,
        "number_of_original_bs": si.number_of_original_bs,
    }
