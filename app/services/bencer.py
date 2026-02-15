from sqlalchemy.orm import Session
from app.repositories.lc_repo import LCRepo
from app.repositories.vehicle_register import VehicleRegisterRepo
from app.schemas.bencer import BencerGenerate
import jinja2
import os
from weasyprint import HTML
from datetime import datetime
from app.repositories.commercial_invoice import CommercialInvoiceRepo
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionUpdate
from app.schemas.bencer import CreateBencer
from app.repositories.bencer import BencerRepo


def generate_bencer(db: Session, payload: BencerGenerate):
    lc = LCRepo.get_by_id(db, payload.lc_id)
    vr = VehicleRegisterRepo.get_by_id(db, payload.vehicle_register_id)
    commcercial_invoice = CommercialInvoiceRepo.get_by_id(
        db, payload.commercial_invoice_id
    )
    template_path = r"E:\\job\\autoship-hub-server\\app\\templates\\bencer.html"
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    # logo_path should be a file:// URL for WeasyPrint on Windows
    logo_file_path = r"E:\\job\\autoship-hub-server\\app\\assets\\logopap.png"
    logo_url = "file:///" + logo_file_path.replace("\\", "/")
    for i in (lc.document_require_46a or {}).get("items", []):
        if i.get("doc_type") == "BENEFICIARY_CERTIFICATE":
            beneficiary_to_certify = i.get("conditions", "")

    html_out = template.render(
        logo_url=logo_url,
        lc_credit_number=lc.docmentary_credit_number_20,
        date_of_issue=lc.date_of_issue_31c,
        chassis_no=vr.chassis_no,
        engine_no=vr.engine_no,
        date=payload.date,
        director=payload.director,
        bank=commcercial_invoice.bank,
        beneficiary_to_certify=beneficiary_to_certify,
    )
    # Ensure output directory exists
    output_dir = r"E:\\job\\autoship-hub-server\\app\\pdf"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate filename
    filename = f"bencer_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join(output_dir, filename)
    # Convert to PDF using WeasyPrint
    # Providing base_url helps resolve relative assets if any
    HTML(string=html_out, base_url=template_dir).write_pdf(output_path)
    TransactionRepo.update(
        db,
        payload.transaction_id,
        TransactionUpdate(status="pending", current_process="bencer"),
    )
    return {"output_path": output_path}


def confirm_bencer(db: Session, payload: CreateBencer, user_id: int):
    bencer = BencerRepo.create(db, payload, user_id)
    TransactionRepo.update(
        db,
        payload.transaction_id,
        TransactionUpdate(
            status="completed", current_process="bencer", bencer_id=bencer.id
        ),
    )
    return bencer
