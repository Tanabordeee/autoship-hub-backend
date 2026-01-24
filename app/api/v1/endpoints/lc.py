from fastapi import APIRouter, File, UploadFile, Depends , Form, Body
from sqlalchemy.orm import Session
from app.services.lc import extract_lc
from app.api.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.lc import LCCreate, LC
from app.services.lc import create_lc
from app.services.lc import generate_excel
from fastapi.responses import FileResponse
from app.services.lc.lc_boundary import boundary_text
from app.schemas.lc import LCBoundary
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

@router.post("/create-lc", response_model=LC)
def create_lc_endpoint(
    payload: LCCreate,
    pi_id: list[int] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_lc(db , payload , current_user.id , pi_id)

@router.get("/lc-excel/{id}")
def generate_excel_endpoint(id:int , db:Session = Depends(get_db) , current_user: User = Depends(get_current_user)):
    file_path = generate_excel(db, id)
    return FileResponse(
        path=file_path,
        filename=f"LC_{id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

