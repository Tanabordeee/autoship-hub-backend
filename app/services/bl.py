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
from app.repositories.bl import BLRepository
from app.schemas.bl import BLCreate
from bs4 import BeautifulSoup


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
    if not data["port_of_discharge"]:
        data["port_of_discharge"] = extract_single(
            text, r"Place of Delivery\s*\n\s*([A-Z ,]+)\s*\/"
        )
    data["freight_payable_at"] = extract_single(
        text, r"Freight Payable at\s*\n(.*?)(?=\n[A-Z][A-Za-z /]{3,}\n|\n\n|$)"
    )

    data["number_of_original_bs"] = extract_single(
        text, r"Number of Original Bs\/L\s*\n\s*([^\n\/]+)"
    )
    data["gross_weight"] = extract_single(text, r"(\d{1,3}(?:,\d{3})*\.\d+\s*KGS)")

    data["measurement"] = extract_single(text, r"(\d+\.\d+\s*CBM)")

    data["shipper"] = extract_block(text, "Shipper")
    data["consignee"] = extract_block(text, "Consignee")
    data["notify_party"] = extract_block(text, "Notify Party")
    data["cy_cf"] = extract_single(text, r"SHIPPED\s+ON\s+BOARD\s*:\s*([^</]+)")
    soup = BeautifulSoup(text, "html.parser")
    table = soup.find("table")

    rows = table.find_all("tr")
    headers = [td.get_text(strip=True) for td in rows[0].find_all("td")]

    desc_idx = headers.index("Description of Packages and Goods")
    data["description_of_good"] = (
        rows[1].find_all("td")[desc_idx].get_text(" ", strip=True)
    )
    container_match = re.search(
        r"([A-Z]{4}\d{7})\/(\d{6,})\/([0-9]{2}'(?:HQ|GP|RF))", text
    )
    if container_match:
        data["container"] = container_match.group(1)
        data["seal_no"] = container_match.group(2)
        data["size_no"] = container_match.group(3)
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
    data["text"] = text
    return data


def confirm_bl(db: Session, transaction_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="confirm", current_process="bl"),
        )
    except Exception as e:
        print(e)
    return True


def reject_bl(db: Session, transaction_id: int):
    try:
        TransactionRepo.update(
            db,
            int(transaction_id),
            TransactionUpdate(status="reject", current_process="bl"),
        )
    except Exception as e:
        print(e)
    return True


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
    return BLRepository.create(db, payload)
