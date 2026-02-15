from fastapi import APIRouter
from app.api.deps import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.services.transaction import (
    get_all_transactions,
    get_transaction_logs,
    get_all_logs,
)
from app.schemas.audit_log import AuditLogResponse
from typing import List

router = APIRouter()


@router.get("/transactions")
def get_all_transactions_endpoint(db: Session = Depends(get_db)):
    return get_all_transactions(db)


@router.get(
    "/transactions/{transaction_id}/logs", response_model=List[AuditLogResponse]
)
def get_transaction_logs_endpoint(transaction_id: int, db: Session = Depends(get_db)):
    return get_transaction_logs(db, transaction_id)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_all_logs_endpoint(db: Session = Depends(get_db)):
    return get_all_logs(db)
