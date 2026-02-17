from sqlalchemy.orm import Session, joinedload
from app.models.user import User


class UserRepository:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, id: int):
        from app.models.transaction import Transaction

        return (
            db.query(User)
            .options(
                joinedload(User.transactions).joinedload(Transaction.proforma_invoice)
            )
            .filter(User.id == id)
            .first()
        )

    def create(self, db: Session, email: str, password: str, role: str, name: str):
        user = User(email=email, password=password, role=role, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_all(self, db: Session):
        return db.query(User).all()

    def update(self, db: Session, user_id: int, payload: dict):
        user = self.get_by_id(db, user_id)
        if user:
            for key, value in payload.items():
                if value is not None:
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user

    def delete(self, db: Session, user_id: int):
        user = self.get_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    def get_all_approver(self, db: Session):
        return db.query(User).filter(User.role == "employee").all()


user_repo = UserRepository()
