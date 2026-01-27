from fastapi import APIRouter, Depends, UploadFile, File, Form, Body
from app.api.deps import get_db

# from app.services.booking_service import create_booking
from app.services.booking.service import extract_booking

# from app.schemas.booking import CreateBooking
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.booking import CreateBooking
from app.services.booking.service import create_booking

router = APIRouter()


@router.post("/bookings")
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


@router.post("/extract-booking")
def extract_booking_endpoint(
    transaction_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return extract_booking(db, file, transaction_id)
