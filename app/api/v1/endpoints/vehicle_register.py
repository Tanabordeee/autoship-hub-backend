from fastapi import APIRouter, File, UploadFile, Depends, Form, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.vehicle_register import (
    extract_vehicle_register,
    create_vehicle_register,
    create_vehicle_register_excel,
)
from app.schemas.vehicle_register import (
    VehicleRegisterCreate,
    VehicleRegisterCreateResponse,
)

router = APIRouter()


@router.post("/extract-vehicle-register")
def extract_vehicle_register_endpoint(
    transaction_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return extract_vehicle_register(db, file, transaction_id)


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_path = create_vehicle_register_excel(db, id)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"vehicle_register_{id}.xlsx",
    )
