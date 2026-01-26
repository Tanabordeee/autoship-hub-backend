from fastapi import APIRouter, Depends, UploadFile, File
from app.api.deps import get_db

# from app.services.booking_service import create_booking
from app.services.booking.service import extract_booking

# from app.schemas.booking import CreateBooking
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


# @router.post("/bookings", response_model=str)
# def create_booking_endpoint(
#     payload: CreateBooking,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     return create_booking(db, payload, current_user.id)


@router.post("/extract-booking")
def extract_booking_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return extract_booking(file)
