from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from app.schemas.transaction import TransactionUpdate
from app.models.user import User


class TransactionRepo:
    def create(db: Session, payload: TransactionCreate, user_id: int = None):

        transaction = Transaction(
            status=payload.status, current_process=payload.current_process
        )
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user not in transaction.users:
                transaction.users.append(user)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def update(db: Session, id: int, payload: TransactionUpdate, user_id: int = None):
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
        if payload.insurance_id:
            transaction.insurance_id = payload.insurance_id
        if payload.commercial_invoice_id:
            transaction.commercial_invoice_id = payload.commercial_invoice_id
        if payload.bencer_id:
            transaction.bencer_id = payload.bencer_id
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user not in transaction.users:
                transaction.users.append(user)
        db.commit()
        db.refresh(transaction)
        return transaction
