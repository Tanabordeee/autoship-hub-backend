from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.user_repo import user_repo
from app.core.security import hash_password
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserUpdate


def create_user(
    db: Session, user_email: str, user_password: str, user_role: str, user_name: str
):
    if user_repo.get_by_email(db, user_email):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = hash_password(user_password)
    return user_repo.create(
        db=db, email=user_email, password=hashed_pwd, role=user_role, name=user_name
    )


def get_all_approver(db: Session):
    return user_repo.get_all_approver(db)


def get_user_transactions(db: Session, user_id: int):
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.transactions


def get_all_users(db: Session):
    return user_repo.get_all(db)


def get_user_by_id(db: Session, user_id: int):
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(db: Session, user_id: int, user_update: "UserUpdate"):
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    user = user_repo.update(db, user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def delete_user(db: Session, user_id: int):
    success = user_repo.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
