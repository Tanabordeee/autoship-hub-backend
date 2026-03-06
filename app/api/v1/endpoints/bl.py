from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    Body,
    BackgroundTasks,
    HTTPException,
)
import os
import uuid
from app.api.deps import get_db, get_current_user
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.bl import extract_bl, get_check_data, process_bl_extraction
from app.schemas.bl import BLCheck
from app.services.bl import create_bl, confirm_bl, reject_bl, get_bl_by_id
from app.schemas.bl import (
    BLCreate,
    BL,
    TransactionStatusUpdateConfirm,
    TransactionStatusUpdateReject,
    BL_id,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate

router = APIRouter()


@router.post("/extract-bl")
async def extract_bl_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous BL extraction job
    """
    # 1. Save uploaded file
    upload_dir = "app/pdf"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 2. Create extraction job record
    job_id = str(uuid.uuid4())
    job_data = ExtractionJobCreate(
        id=job_id,
        transaction_id=int(transaction_id),
        user_id=current_user.id,
        status="pending",
    )
    ExtractionJobRepo.create(db, job_data)

    # 3. Add to background tasks
    background_tasks.add_task(
        process_bl_extraction,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=int(transaction_id),
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-bl-status/{job_id}")
def get_extraction_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the status and result of an extraction job
    """
    job = ExtractionJobRepo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")

    return {
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.post("/get-check-bl")
def get_check_bl_endpoint(
    payload: BLCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_check_data(db, payload)


@router.post("/create-bl", response_model=BL)
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
    return confirm_bl(db, payload.transaction_id, payload.bl_id, current_user.id)


@router.post("/reject-bl")
def reject_bl_endpoint(
    payload: TransactionStatusUpdateReject = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_bl(db, payload.transaction_id, current_user.id)


@router.post("/bl-all-version")
def get_all_bl_versions(
    payload: BL_id,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_bl_by_id(db, payload.id)
