import pdfplumber
import re
from app.repositories.booking import BookingRepo
from app.schemas.booking import CreateBooking
from sqlalchemy.orm import Session
from app.repositories.transaction_repo import TransactionRepo
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.schemas.transaction import TransactionUpdate


def extract_booking(db: Session, file, transaction_id: int):
    text = ""
    file.file.seek(0)
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    def safe_search(pattern, content, group_idx=1):
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            return (
                match.group(group_idx).strip()
                if match.groups()
                else match.group(0).strip()
            )
        return None

    # Extraction patterns based on user's template
    # Note: Using \s* and [\n\r] for flexibility
    result = {
        "date": safe_search(r"Date\s*:\s*(.*?)(?=\n|$)", text),
        "booking_no": safe_search(r"Booking\n?\s*No\.\s*:\s*(.*?)(?=\n|$)", text),
        "carrier_booking_no": safe_search(
            r"Carrier\s*Booking\s*No\s*:\s*(.*?)(?=\n|$)", text
        ),
        "carrier": safe_search(r"Carrier\s*:\s*(.*?)(?=\n|$)", text),
        "shipper": safe_search(r"Shipper\s*:\s*(.*?)(?=\n|$)", text),
        "consignee": safe_search(r"Consignee\s*:\s*(.*?)(?=\n|$)", text),
        "fob_at": safe_search(r"FOB\s*at\s*:\s*(.*?)(?=\n|$)", text),
        "quantity": safe_search(r"Quantities\s*:\s*(.*?)(?=\n|$)", text),
        "feeder": safe_search(r"Feeder\s*:\s*(.*?)(?=\n|$)", text),
        "vessel": safe_search(r"Vessel\s*:\s*(.*?)(?=\n|$)", text),
        "place_of_rec": safe_search(r"Place\s*of\s*Rec\.\s*:\s*(.*?)(?=\n|$)", text),
        "port_of_loading": safe_search(
            r"Port\s*of\s*Loading\s*:\s*(.*?)(?=\s*ETD|$)", text
        ),
        "etd": safe_search(r"ETD\s*:\s*(.*?)(?=\n|$)", text),
        "ts_port": safe_search(r"T/S\s*Port\s*:\s*(.*?)(?=\n|$)", text),
        "port_of_disch": safe_search(
            r"Port\s*of\s*Disch\.\s*:\s*(.*?)(?=\s*ETA Dest|$)", text
        ),
        "eta_dest": safe_search(r"ETA\s*Dest\.\s*:\s*(.*?)(?=\n|$)", text),
        "port_of_del": safe_search(r"Port\s*of\s*Del\.\s*:\s*(.*?)(?=\n|$)", text),
        "final_destn": safe_search(r"Final\s*Destn\.\s*:\s*(.*?)(?=\n|$)", text),
        "cy_date": safe_search(r"CY\s*Date\s*:\s*(.*?)(?=\n|$)", text),
        "cy_at": safe_search(r"CY\s*AT\s*:\s*(.*?)(?=\n|$)", text),
        "first_date_return": safe_search(
            r"1st\s*Date\s*Return\s*:\s*(.*?)(?=\n|$)", text
        ),
        "return_date": safe_search(r"Return\s*Date\s*:\s*(.*?)(?=\n|$)", text),
        "return_yard": safe_search(r"Return\s*Yard\s*:\s*(.*?)(?=\n|$)", text),
        "paperless_code": safe_search(r"Paperless\s*Code\s*:\s*(.*?)(?=\n|$)", text),
        "closing_date": safe_search(
            r"Closing\s*Date\s*:\s*(.*?)(?=\s*At Before|$)", text
        ),
        "at_before": safe_search(r"At\s*Before\s*:\s*(.*?)(?=\n|$)", text),
        "cut_off_si": safe_search(r"Cut\s*Off\s*SI\s*:\s*(.*?)(?=\n|$)", text),
        "cut_off_vgm": safe_search(r"Cut\s*Off\s*VGM\s*:\s*(.*?)(?=\n|$)", text),
        "booking_name": safe_search(r"(RIVA\s*LOGISTICS\s*CO\.,LTD\.)", text),
    }
    TransactionRepo.update(
        db,
        transaction_id,
        TransactionUpdate(status="pending", current_process="booking"),
    )
    return result


def create_booking(
    db: Session, payload: CreateBooking, user_id: int, transaction_id: int
):
    booking = BookingRepo.create(db, payload, user_id)
    ProformaInvoiceRepo.update_booking_pi_items(db, payload.chassis, booking.id)
    TransactionRepo.update(
        db,
        transaction_id,
        TransactionUpdate(status="completed", current_process="booking"),
    )
    return booking
