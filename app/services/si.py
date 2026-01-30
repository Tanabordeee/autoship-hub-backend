from sqlalchemy.orm import Session
from app.repositories.si import SI_Repository
from app.schemas.si import SICreate
from app.repositories.lc_repo import LCRepo
from app.repositories.booking import BookingRepo
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from weasyprint import HTML, CSS
import jinja2
import os
import re
from datetime import datetime
import logging
import num2words

logger = logging.getLogger(__name__)


def create_si(db: Session, payload: SICreate):
    si = SI_Repository.create_si(db, payload)
    lc = LCRepo.get_by_id(db, payload.lc_id)
    booking = BookingRepo.get_by_id(db, payload.booking_id)
    vehicle_register = VehicleRegisterRepo.get_by_id(db, payload.vehicle_register_id)
    proforma_invoice = ProformaInvoiceRepo.get_by_id(db, payload.pi_id)
    if not si or not lc or not booking or not vehicle_register or not proforma_invoice:
        return None
    logger.info("description_of_good_45a_45b: %s", lc.description_of_good_45a_45b)
    item_first_text = lc.document_require_46a["items"][0]["conditions"]
    match = re.search(
        r"(?:AS\s*)?PER\s*PROFORMA\s*INVOICE\s*NO\.?\s*[A-Z0-9-]+\s*OF\s*\d{1,2}\.\d{1,2}\.\d{4}",
        item_first_text,
    )
    as_per_proforma_invoice = match.group(0) if match else ""
    date_str = booking.etd
    dt = datetime.strptime(date_str, "%d/%m/%Y")
    etd = dt.strftime("%B %d, %Y").upper()
    number_of_original_bs = num2words.num2words(
        payload.number_of_original_bs, lang="en"
    ).upper()
    # Setup Jinja2
    template_path = r"E:\\job\\autoship-hub-server\\app\\templates\\si.html"
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    # Render HTML
    html_out = template.render(
        si=si,
        lc=lc,
        port_of_discharge=payload.port_of_discharge,
        port_of_loading=payload.port_of_loading,
        gross_weight=payload.gross_weight,
        measurement=payload.measurement,
        no_of_packages=payload.no_of_packages,
        number_of_original_bs=number_of_original_bs,
        original_bs=payload.number_of_original_bs,
        booking=booking,
        vehicle_register=vehicle_register,
        proforma_invoice=proforma_invoice,
        as_per_proforma_invoice=as_per_proforma_invoice,
        etd=etd,
    )
    # Convert to PDF using WeasyPrint
    output_path = payload.output_path
    if os.path.isdir(output_path):
        filename = f"si_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = os.path.join(output_path, filename)

    css_path = os.path.join(os.getcwd(), "static", "tailwind.css")

    stylesheets = []
    if os.path.exists(css_path):
        stylesheets.append(CSS(filename=css_path))

    HTML(string=html_out).write_pdf(output_path, stylesheets=stylesheets)
    TransactionRepo.update(
        db,
        payload.transaction_id,
        TransactionUpdate(status="pending", current_process="si"),
    )
    return output_path


def confirm_si(db: Session, transaction_id: int):
    TransactionRepo.update(
        db,
        transaction_id,
        TransactionUpdate(status="completed", current_process="si"),
    )
    return True
