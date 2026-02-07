from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.services.bl import extract_bl, get_check_data
from app.schemas.bl import BLCheck
from app.services.bl import create_bl, confirm_bl, reject_bl
from app.schemas.bl import (
    BLCreate,
    TransactionStatusUpdateConfirm,
    TransactionStatusUpdateReject,
)

router = APIRouter()


@router.post("/extract-bl")
def extract_bl_endpoint(
    transaction_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = extract_bl(db, file, transaction_id)
    return result


@router.post("/get-check-bl")
def get_check_bl_endpoint(
    payload: BLCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_check_data(db, payload)


@router.post("/create-bl")
def create_bl_endpoint(
    payload: BLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_bl(db, payload)


@router.post("/confirm-bl")
def confirm_bl_endpoint(
    payload: TransactionStatusUpdateConfirm = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return confirm_bl(db, payload.transaction_id, payload.bl_id)


@router.post("/reject-bl")
def reject_bl_endpoint(
    payload: TransactionStatusUpdateReject = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_bl(db, payload.transaction_id)
