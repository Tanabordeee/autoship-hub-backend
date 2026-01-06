from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.repositories.user_repo import user_repo

# token = oauth2_scheme() อ่าน header Authorization ตรวจว่ามี Bearer ไหม ตัดคำว่า Bearer return ค่า token เป็น str
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login") # tokenUrl บอก Swagger UI

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_repo.get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    '''
    __call__ คืออะไร
    class A:
        def __call__(self):
            print("called")


    ทำให้ object ถูกเรียกเหมือน function

    a = A()
    a()   # → __call__ ถูกเรียก

    ถูกเรียก ตอนใช้งาน

    '''
    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
