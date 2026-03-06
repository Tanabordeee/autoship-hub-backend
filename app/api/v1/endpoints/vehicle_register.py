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
import os
import uuid
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.vehicle_register import (
    extract_vehicle_register,
    create_vehicle_register,
    create_vehicle_register_excel,
    get_vehicle_register_by_id,
    process_vehicle_register_extraction,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate
from app.schemas.vehicle_register import (
    VehicleRegisterCreate,
    VehicleRegisterCreateResponse,
    VehicleRegisterID,
)

router = APIRouter()


@router.post("/extract-vehicle-register")
async def extract_vehicle_register_endpoint(
    background_tasks: BackgroundTasks,
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous Vehicle Register extraction job
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
        process_vehicle_register_extraction,
        job_id=job_id,
        file_path=file_path,
        user_id=current_user.id,
        transaction_id=transaction_id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/extract-vehicle-register-status/{job_id}")
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


@router.post("/vehicle-register", response_model=VehicleRegisterCreateResponse)
def create_vehicle_register_endpoint(
    payload: VehicleRegisterCreate = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_vehicle_register(db, payload, current_user.id, payload.transaction_id)


@router.get("/vehicle-register-excel/{id}")
def create_vehicle_register_excel_endpoint(
    id: int,
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = create_vehicle_register_excel(db, id, transaction_id, current_user.id)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"vehicle_register_{id}.xlsx",
    )


@router.post("/get-vehicle-register")
def get_vehicle_register_by_id_endpoint(
    payload: VehicleRegisterID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_vehicle_register_by_id(db, payload.id)
