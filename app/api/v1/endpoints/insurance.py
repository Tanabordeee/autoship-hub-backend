from fastapi import APIRouter, File, Form, UploadFile, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_current_user, get_db
from app.services.insurance import extract_insurance, get_check_insurance
from app.schemas.insurance import InsuranceCheck

router = APIRouter()


@router.post("/extract-insurance")
def extract_insurance_endpoint(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = extract_insurance(db, file, transaction_id)
    return result


@router.post("/check-insurance")
def check_insurance_endpoint(
    payload: InsuranceCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_check_insurance(db, payload)
    return result
