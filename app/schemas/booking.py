from pydantic import BaseModel
from typing import Optional
from datetime import date


class CreateBooking(BaseModel):
    booking_id: str
    booking_date: date
    customer_id: int
    at_before: Optional[date] = None
    cut_off_vgm: Optional[date] = None
    cut_off_si: Optional[date] = None
    booking_name: Optional[str] = None
    etd: Optional[date] = None
    fob_at_quantities: Optional[str] = None
    consignee: Optional[str] = None
    return_date: Optional[date] = None
    cy_date: Optional[date] = None
    cy_at: Optional[str] = None
    carrier: Optional[str] = None
    closing_date: Optional[date] = None
    port_of_disch: Optional[str] = None
    shipper: Optional[str] = None
    port_of_del: Optional[str] = None
    return_yard: Optional[str] = None
    port_of_loading: Optional[str] = None
    eta_date: Optional[date] = None
    feeder: Optional[str] = None
    place_of_rec: Optional[str] = None
    paperless_code: Optional[str] = None
    lc_id: Optional[int] = None
    transaction_id: Optional[int] = None


class Booking(BaseModel):
    booking_id: str
    booking_date: date
    customer_id: int
    at_before: Optional[date] = None
    cut_off_vgm: Optional[date] = None
    cut_off_si: Optional[date] = None
    booking_name: Optional[str] = None
    etd: Optional[date] = None
    fob_at_quantities: Optional[str] = None
    consignee: Optional[str] = None
    return_date: Optional[date] = None
    cy_date: Optional[date] = None
    cy_at: Optional[str] = None
    carrier: Optional[str] = None
    closing_date: Optional[date] = None
    port_of_disch: Optional[str] = None
    shipper: Optional[str] = None
    port_of_del: Optional[str] = None
    return_yard: Optional[str] = None
    port_of_loading: Optional[str] = None
    eta_date: Optional[date] = None
    feeder: Optional[str] = None
    place_of_rec: Optional[str] = None
    paperless_code: Optional[str] = None
    lc_id: Optional[int] = None
    transaction_id: Optional[int] = None
