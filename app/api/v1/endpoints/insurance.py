from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_current_user, get_db
from app.services.insurance import extract_insurance

router = APIRouter()


@router.post("/extract-insurance")
def extract_insurance_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = extract_insurance(db, file)
    return result
