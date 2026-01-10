from sqlalchemy.orm import Session
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.schemas.proforma_invoice import CreateProformaInvoice
import os
import jinja2
from weasyprint import HTML
def create_proforma_invoice(db:Session, payload:CreateProformaInvoice , user_id:int):
    return ProformaInvoiceRepo.create(db, payload, user_id)


def generate_pdf(pi_id: int , db: Session, output_path: str):
    pi = ProformaInvoiceRepo.get_by_id(db, pi_id)
    if not pi:
        raise Exception("Proforma Invoice not found")

    # Setup Jinja2
    template_path = r"E:\\job\\autoship-hub-server\\app\\templates\\invoice_weasy.html"
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_file)
    
    # Render HTML
    html_out = template.render(invoice=pi)
    
    # Convert to PDF using WeasyPrint
    HTML(string=html_out).write_pdf(output_path)
    return output_path

def approve_proforma_invoice(db:Session, pi_id:int , approver:str):
    return ProformaInvoiceRepo.update_pi_status(db, pi_id, "approved", approver)


def reject_proforma_invoice(db:Session, pi_id:int):
    return ProformaInvoiceRepo.update_pi_status(db, pi_id, "rejected")