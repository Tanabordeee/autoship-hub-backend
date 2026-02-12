from sqlalchemy.orm import Session
from app.schemas.commercial_invoice import CreateCommercialInvoicePayload
from app.models.commercial_invoice import CommercialInvoice


class CommercialInvoiceRepo:
    def create(db: Session, payload: CreateCommercialInvoicePayload, user_id: int):
        commercial_invoice = CommercialInvoice(
            director=payload.director,
            bank=payload.bank,
            user_id=user_id,
        )
        db.add(commercial_invoice)
        db.commit()
        db.refresh(commercial_invoice)
        return commercial_invoice
