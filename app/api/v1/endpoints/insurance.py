from fastapi import (
    APIRouter,
    File,
    Form,
    UploadFile,
    Depends,
    BackgroundTasks,
    HTTPException,
)
import os
import uuid
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_current_user, get_db
from app.services.insurance import (
    extract_insurance,
    get_check_insurance,
    create_insurance,
    confirm_insurance,
    reject_insurance,
    get_insurance_by_id,
    process_insurance_extraction,
)
from app.schemas.insurance import (
    InsuranceCheck,
    InsuranceCreate,
    Insurance,
    InsuranceConfirm,
    Insurance_id,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate

router = APIRouter()


@router.post("/extract-insurance")
async def extract_insurance_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous Insurance extraction job
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
        process_insurance_extraction,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=transaction_id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-insurance-status/{job_id}")
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


@router.post("/check-insurance")
def check_insurance_endpoint(
    payload: InsuranceCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = get_check_insurance(db, payload)
    return result


@router.post("/create-insurance", response_model=Insurance)
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
def get_all_insurance_versions(
    payload: Insurance_id,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_insurance_by_id(db, payload.id)
