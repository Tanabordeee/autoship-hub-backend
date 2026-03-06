from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import os
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.commercial_invoice import (
    generate_commercial_invoice,
    generate_commercial_invoice_excel,
    confirm_commercial_invoice,
    process_commercial_invoice_generation,
    process_commercial_invoice_excel_generation,
)
from app.schemas.commercial_invoice import (
    CommercialInvoice,
    CommercialInvoiceResponse,
    CreateCommercialInvoicePayload,
)
from app.repositories.extraction_job_repo import ExtractionJobRepo
from app.schemas.extraction_job import ExtractionJobCreate

router = APIRouter()


@router.post("/commercial_invoice")
async def generate_commercial_invoice_endpoint(
    background_tasks: BackgroundTasks,
    payload: CommercialInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous Commercial Invoice (PDF) generation job
    """
    job_id = str(uuid.uuid4())
    job_data = ExtractionJobCreate(
        id=job_id,
        transaction_id=payload.transaction_id,
        user_id=current_user.id,
        status="pending",
    )
    ExtractionJobRepo.create(db, job_data)

    background_tasks.add_task(
        process_commercial_invoice_generation,
        job_id=job_id,
        payload=payload,
        user_id=current_user.id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.post("/commercial_invoice_excel")
async def generate_commercial_invoice_excel_endpoint(
    background_tasks: BackgroundTasks,
    payload: CommercialInvoice,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Start an asynchronous Commercial Invoice (Excel) generation job
    """
    job_id = str(uuid.uuid4())
    job_data = ExtractionJobCreate(
        id=job_id,
        transaction_id=payload.transaction_id,
        user_id=current_user.id,
        status="pending",
    )
    ExtractionJobRepo.create(db, job_data)

    background_tasks.add_task(
        process_commercial_invoice_excel_generation,
        job_id=job_id,
        payload=payload,
        user_id=current_user.id,
    )

    return {"job_id": job_id, "status": "pending"}


@router.get("/commercial-invoice-status/{job_id}")
def get_generation_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the status and result of a generation job
    """
    job = ExtractionJobRepo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this job")

    # If completed, the result will contain {"output_path": "..."}
    # User can then use another endpoint to download if needed,
    # but usually they return the path to the frontend.
    return {
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "error": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


@router.post("/confirm_commercial_invoice", response_model=CommercialInvoiceResponse)
def confirm_commercial_invoice_endpoint(
    payload: CreateCommercialInvoicePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = confirm_commercial_invoice(db, payload, current_user.id)
    if result:
        return result
    return {"error": "Failed to confirm commercial invoice"}


@router.get("/download-file")
def download_file(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path, filename=os.path.basename(path), media_type="application/octet-stream"
    )
