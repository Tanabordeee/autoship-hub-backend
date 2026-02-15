from sqlalchemy.orm import Session
from app.repositories.transaction_repo import TransactionRepo


def get_all_transactions(db: Session):
    return TransactionRepo.get_all(db)
