from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories.user_repo import user_repo
from app.core.security import verify_password, create_access_token


def login(email: str, password: str, db: Session):
    user = user_repo.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    token = create_access_token(
        {"id": user.id, "email": user.email, "role": user.role, "name": user.name}
    )
    return {"token": token}
