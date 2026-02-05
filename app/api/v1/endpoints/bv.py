from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.bv import extract_bv
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.bv import BVCreate, BVCheck
from app.services.bv import create_bv, confirm_bv, reject_bv, get_check_bv

router = APIRouter()


@router.post("/extract-bv")
def extract_bv_endpoint(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return extract_bv(db, file, transaction_id)


@router.post("/create-bv")
def create_bv_endpoint(
    payload: BVCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_bv(db, payload)


@router.post("/confirm-bv")
def confirm_bv_endpoint(
    transaction_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return confirm_bv(db, transaction_id)


@router.post("/reject-bv")
def reject_bv_endpoint(
    transaction_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_bv(db, transaction_id)


@router.post("/check-bv")
def check_bv_endpoint(
    payload: BVCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_check_bv(db, payload.chassis)
