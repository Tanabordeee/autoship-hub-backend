from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Depends,
    Form,
    Body,
    BackgroundTasks,
    HTTPException,
)
from sqlalchemy.orm import Session
import os
import uuid
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.lc import LCCreate, LC, LC_id
from app.services.lc import (
    create_lc,
    generate_excel,
    get_lc_by_id,
    process_extraction_job,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate
from fastapi.responses import FileResponse

router = APIRouter()


@router.post("/extract-lc")
async def extract_lc_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous LC extraction job
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
        process_extraction_job,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=transaction_id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-lc-status/{job_id}")
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

    # Optional: check if job belongs to current user
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


@router.post("/create-lc", response_model=LC)
def create_lc_endpoint(
    payload: LCCreate,
    pi_id: list[int] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_lc(db, payload, current_user.id, pi_id)


@router.get("/lc-excel/{id}")
def generate_excel_endpoint(
    id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = generate_excel(db, id, transaction_id, current_user.id)
    return FileResponse(
        path=file_path,
        filename=f"LC_{id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/lc-all-version", response_model=list[LC])
def get_all_lc_versions(
    payload: LC_id,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_lc_by_id(db, payload.id)
