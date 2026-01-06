from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.user_repo import user_repo
from app.core.security import hash_password

def create_user(db: Session, user_email: str, user_password: str , user_role:str):
    if user_repo.get_by_email(db, user_email):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = hash_password(user_password)
    return user_repo.create(
        db=db,
        email=user_email,
        password=hashed_pwd,
        role=user_role
    )
