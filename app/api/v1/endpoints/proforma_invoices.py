from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.proforma_invoice_service import create_proforma_invoice
from app.api.deps import get_db
from app.schemas.proforma_invoice import CreateProformaInvoice
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User
router = APIRouter()

@router.post("/proforma_invoices", response_model=CreateProformaInvoice)
def create_proforma_invoice_endpoint(payload: CreateProformaInvoice , db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_proforma_invoice(db, payload, current_user.id)