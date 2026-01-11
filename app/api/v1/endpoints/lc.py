from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.orm import Session
from app.services.lc import extract_lc
from app.api.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/extract-lc")
def extract_lc_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Extract LC data from uploaded PDF file and return as JSON
    """
    extracted_data = extract_lc(db, file, current_user.id)
    return extracted_data