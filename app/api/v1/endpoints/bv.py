from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    HTTPException,
)
import os
import uuid
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.bv import BVCreate, BVCheck, ConfirmAndRejectBV, BVResponse, BV_id
from app.services.bv import (
    create_bv,
    confirm_bv,
    reject_bv,
    get_check_bv,
    get_bv_by_id,
    process_bv_extraction,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate

router = APIRouter()


@router.post("/extract-bv")
async def extract_bv_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous BV extraction job
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
        transaction_id=transaction_id,
        user_id=current_user.id,
        status="pending",
    )
    ExtractionJobRepo.create(db, job_data)

    # 3. Add to background tasks
    background_tasks.add_task(
        process_bv_extraction,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=transaction_id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-bv-status/{job_id}")
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


@router.post("/create-bv", response_model=BVResponse)
def create_bv_endpoint(
    payload: BVCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_bv(db, payload, payload.transaction_id, current_user.id)


@router.post("/confirm-bv")
def confirm_bv_endpoint(
    payload: ConfirmAndRejectBV,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return confirm_bv(db, payload.transaction_id, current_user.id)


@router.post("/reject-bv")
def reject_bv_endpoint(
    payload: ConfirmAndRejectBV,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_bv(db, payload.transaction_id, current_user.id)


@router.post("/check-bv")
def check_bv_endpoint(
    payload: BVCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_check_bv(db, payload.chassis)


@router.post("/bv-all-version")
def get_all_bv_versions(
    payload: BV_id,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_bv_by_id(db, payload.id)
