from sqlalchemy.orm import Session
from app.repositories.transaction_repo import TransactionRepo
from app.services.audit_log_service import audit_log_service


def get_all_transactions(db: Session):
    return TransactionRepo.get_all(db)


def get_transaction_logs(db: Session, transaction_id: int):
    return audit_log_service.get_transaction_logs(db, transaction_id)


def get_all_logs(db: Session):
    return audit_log_service.list_logs(db)
