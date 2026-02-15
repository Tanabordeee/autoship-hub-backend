from pydantic import BaseModel
from typing import Optional


class TransactionCreate(BaseModel):
    status: str
    current_process: str


class TransactionUpdate(BaseModel):
    status: str
    current_process: str
    lc_id: Optional[int] = None
    si_id: Optional[int] = None
    bl_id: Optional[int] = None
    insurance_id: Optional[int] = None
    commercial_invoice_id: Optional[int] = None
    bencer_id: Optional[int] = None
    booking_id: Optional[int] = None
    vehicle_register_id: Optional[int] = None
    bv_id: Optional[int] = None
    proforma_invoice_id: Optional[int] = None


class TransactionOut(BaseModel):
    id: int
    status: str
    current_process: str
    lc_id: Optional[int] = None
    si_id: Optional[int] = None
    bl_id: Optional[int] = None
    insurance_id: Optional[int] = None
    commercial_invoice_id: Optional[int] = None
    bencer_id: Optional[int] = None
    booking_id: Optional[int] = None
    vehicle_register_id: Optional[int] = None
    bv_id: Optional[int] = None
    proforma_invoice_id: Optional[int] = None

    class Config:
        from_attributes = True
