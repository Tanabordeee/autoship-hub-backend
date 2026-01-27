from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateBooking(BaseModel):
    at_before: Optional[str] = None
    booking_no: Optional[str] = None
    date: Optional[str] = None
    cut_off_vgm: Optional[str] = None
    cut_off_si: Optional[str] = None
    booking_name: Optional[str] = None
    etd: Optional[str] = None
    fob_at: Optional[str] = None
    quantity: Optional[str] = None
    consignee: Optional[str] = None
    return_date: Optional[str] = None
    cy_date: Optional[str] = None
    cy_at: Optional[str] = None
    carrier: Optional[str] = None
    closing_date: Optional[str] = None
    port_of_disch: Optional[str] = None
    shipper: Optional[str] = None
    port_of_del: Optional[str] = None
    return_yard: Optional[str] = None
    port_of_loading: Optional[str] = None
    eta_dest: Optional[str] = None
    feeder: Optional[str] = None
    place_of_rec: Optional[str] = None
    paperless_code: Optional[str] = None
    lc_id: Optional[int] = None
    chassis: Optional[str] = None
    carrier_booking_no: Optional[str] = None
    transaction_id: Optional[int] = None


class BookingCreateResponse(BaseModel):
    id: int


class Booking(BaseModel):
    id: int
    at_before: Optional[str] = None
    booking_no: Optional[str] = None
    date: Optional[str] = None
    user_id: int
    cut_off_vgm: Optional[str] = None
    cut_off_si: Optional[str] = None
    booking_name: Optional[str] = None
    etd: Optional[str] = None
    consignee: Optional[str] = None
    return_date: Optional[str] = None
    cy_date: Optional[str] = None
    cy_at: Optional[str] = None
    carrier: Optional[str] = None
    closing_date: Optional[str] = None
    port_of_disch: Optional[str] = None
    shipper: Optional[str] = None
    port_of_del: Optional[str] = None
    return_yard: Optional[str] = None
    port_of_loading: Optional[str] = None
    eta_dest: Optional[str] = None
    feeder: Optional[str] = None
    place_of_rec: Optional[str] = None
    paperless_code: Optional[str] = None
    create_at: Optional[datetime] = None
    lc_id: int
    transaction_id: int
    fob_at: Optional[str] = None
    quantity: Optional[str] = None
    carrier_booking_no: Optional[str] = None

    class Config:
        from_attributes = True
