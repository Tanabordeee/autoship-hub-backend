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
from app.api.deps import get_db
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import uuid
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.booking import CreateBooking
from app.services.booking.service import (
    extract_booking,
    get_booking_by_id,
    create_booking,
    create_booking_excel,
    process_booking_extraction,
)
from app.schemas.booking import BookingCreateResponse, Booking_ID
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate

router = APIRouter()


@router.post("/bookings", response_model=BookingCreateResponse)
def create_booking_endpoint(
    payload: CreateBooking = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction_id = payload.transaction_id
    try:
        transaction_id = int(transaction_id)
    except (ValueError, TypeError):
        transaction_id = 0
    return create_booking(db, payload, current_user.id, transaction_id)


@router.get("/booking-excel/{id}")
def booking_excel_endpoint(
    id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = create_booking_excel(db, id, transaction_id, current_user.id)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"booking_{id}.xlsx",
    )


@router.post("/extract-booking")
async def extract_booking_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous Booking extraction job
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
        process_booking_extraction,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=int(transaction_id),
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-booking-status/{job_id}")
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


@router.post("/get-booking")
def get_booking_by_id_endpoint(
    payload: Booking_ID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_booking_by_id(db, payload.id)
