from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction import TransactionUpdate


class TransactionRepo:
    def create(db: Session, payload: TransactionCreate):
        transaction = Transaction(
            status=payload.status, current_process=payload.current_process
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def update(db: Session, id: int, payload: TransactionUpdate):
        transaction = db.query(Transaction).filter(Transaction.id == id).first()
        if not transaction:
            raise BaseException("Transaction not found")
        transaction.status = payload.status
        transaction.current_process = payload.current_process
        if payload.lc_id:
            transaction.lc_id = payload.lc_id
        if payload.si_id:
            transaction.si_id = payload.si_id
        if payload.bl_id:
            transaction.bl_id = payload.bl_id
        db.commit()
        db.refresh(transaction)
        return transaction
