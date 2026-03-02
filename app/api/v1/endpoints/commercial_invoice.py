from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.commercial_invoice import (
    generate_commercial_invoice,
    generate_commercial_invoice_excel,
)
from app.services.commercial_invoice import confirm_commercial_invoice
from app.schemas.commercial_invoice import (
    CommercialInvoice,
    CommercialInvoiceResponse,
    CreateCommercialInvoicePayload,
)

router = APIRouter()


@router.post("/commercial_invoice")
def generate_commercial_invoice_endpoint(
    payload: CommercialInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = generate_commercial_invoice(payload, db, current_user.id)
    if result and "output_path" in result:
        output_path = result["output_path"]
        filename = output_path.split("\\")[-1]
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=filename,
        )
    return {"error": "Failed to generate commercial invoice"}


@router.post("/commercial_invoice_excel")
def generate_commercial_invoice_excel_endpoint(
    payload: CommercialInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = generate_commercial_invoice_excel(db, payload, current_user.id)
    if result and "output_path" in result:
        output_path = result["output_path"]
        filename = output_path.split("\\")[-1]
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
        )
    return {"error": "Failed to generate commercial invoice excel"}


@router.post("/confirm_commercial_invoice", response_model=CommercialInvoiceResponse)
def confirm_commercial_invoice_endpoint(
    payload: CreateCommercialInvoicePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = confirm_commercial_invoice(db, payload, current_user.id)
    if result:
        return result
    return {"error": "Failed to confirm commercial invoice"}
