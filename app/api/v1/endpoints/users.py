from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserOut
from app.services.user_service import create_user, get_all_approver
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User

router = APIRouter()


@router.post("/users", response_model=UserOut)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
    dependencies=[Depends(RoleChecker(["admin"]))],
):
    return create_user(db, user.email, user.password, user.role)


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/approver", response_model=list[UserOut])
def read_users_approver(db: Session = Depends(get_db)):
    return get_all_approver(db)


# สร้าง instance RoleChecker(["admin"])
# dependencies = Dependency ที่ต้องผ่านก่อนเข้า endpoint แต่ “ไม่ส่งค่าเข้า function” ให้ FastAPI เรียกสิ่งนี้ก่อน endpoint
# FastAPI สร้าง instance RoleChecker(["admin"]) และเรียก __call__
@router.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
def read_admin():
    return {"message": "Hello Admin"}
