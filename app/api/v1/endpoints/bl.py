from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.services.bl import extract_bl, get_check_data
from app.schemas.bl import BLCheck

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
