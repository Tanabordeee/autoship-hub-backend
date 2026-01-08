from sqlalchemy.orm import Session
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.schemas.proforma_invoice import CreateProformaInvoice
def create_proforma_invoice(db:Session, payload:CreateProformaInvoice , user_id:int):
    return ProformaInvoiceRepo.create(db, payload, user_id)