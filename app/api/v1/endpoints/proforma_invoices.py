from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import os

from sqlalchemy.orm import Session
from app.services.proforma_invoice_service import create_proforma_invoice, approve_proforma_invoice, reject_proforma_invoice
from app.api.deps import get_db
from app.schemas.proforma_invoice import CreateProformaInvoice, ApproveProformaInvoice
from app.api.deps import get_current_user
from app.models.user import User
from app.services.proforma_invoice_service import generate_pdf

router = APIRouter()

@router.post("/proforma_invoices", response_model=CreateProformaInvoice)
def create_proforma_invoice_endpoint(payload: CreateProformaInvoice, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_proforma_invoice(db, payload, current_user.id)

@router.post("/proforma_invoices/approve/{pi_id}")
def approve_proforma_invoice_endpoint(pi_id: int, payload: ApproveProformaInvoice, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return approve_proforma_invoice(db, pi_id, payload.approver)

@router.post("/proforma_invoices/reject/{pi_id}")
def reject_proforma_invoice_endpoint(pi_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return reject_proforma_invoice(db, pi_id)

@router.get("/proforma_invoices/{pi_id}/pdf")
def generate_pdf_endpoint(pi_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pdf_dir = "E:\\job\\autoship-hub-server\\app\\pdf"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    file_path = os.path.join(pdf_dir, f"invoice_{pi_id}.pdf")
    generate_pdf(pi_id, db, file_path)
    return FileResponse(file_path, media_type="application/pdf", filename=f"invoice_{pi_id}.pdf")