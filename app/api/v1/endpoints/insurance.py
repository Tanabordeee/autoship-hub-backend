from fastapi import APIRouter, File, Form, UploadFile, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_current_user, get_db
from app.services.insurance import (
    extract_insurance,
    get_check_insurance,
    create_insurance,
    confirm_insurance,
    reject_insurance,
    get_insurance_by_id
)
from app.schemas.insurance import InsuranceCheck, InsuranceCreate, InsuranceConfirm , Insurance_id

router = APIRouter()


@router.post("/extract-insurance")
def extract_insurance_endpoint(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = extract_insurance(db, file, transaction_id, current_user.id)
    return result


@router.post("/check-insurance")
def check_insurance_endpoint(
    payload: InsuranceCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_check_insurance(db, payload)
    return result


@router.post("/create-insurance")
def create_insurance_endpoint(
    payload: InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = create_insurance(db, payload, current_user.id)
    return result


@router.post("/confirm-insurance")
def confirm_insurance_endpoint(
    payload: InsuranceConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = confirm_insurance(db, payload, current_user.id)
    return result


@router.post("/reject-insurance")
def reject_insurance_endpoint(
    payload: InsuranceConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = reject_insurance(db, payload, current_user.id)
    return result

@router.post("/insurance-all-version")
def get_all_bv_versions(payload: Insurance_id, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    return get_insurance_by_id(db, payload.id)