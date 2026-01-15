from fastapi import APIRouter, File, UploadFile, Depends , Form, Body
from sqlalchemy.orm import Session
from app.services.lc import extract_lc
from app.api.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.lc import LCCreate
from app.services.lc import create_lc

router = APIRouter()

@router.post("/extract-lc")
def extract_lc_endpoint(
    transaction_id:str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract LC data from uploaded PDF file and return as JSON
    """
    extracted_data = extract_lc(db, file, current_user.id, transaction_id)
    return extracted_data

@router.post("/create-lc")
def create_lc_endpoint(
    payload: LCCreate,
    pi_id: list[int] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_lc(db , payload , current_user.id , pi_id)