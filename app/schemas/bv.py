from pydantic import BaseModel
from typing import Optional


class BVBase(BaseModel):
    type_of_vehicle: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    seat: Optional[str] = None
    commonly_called: Optional[str] = None
    manufacture_grade: Optional[str] = None
    body_colour: Optional[str] = None
    fuel_type: Optional[str] = None
    year_of_manufacture: Optional[str] = None
    inspection_mileage: Optional[str] = None
    engine_capacity: Optional[str] = None
    engine_no: Optional[str] = None
    driving_system: Optional[str] = None
    marks_of_accident_on_chassis: Optional[str] = None
    condition_of_chassis: Optional[str] = None
    country_of_origin: Optional[str] = None
    year_month_of_first_registration: Optional[str] = None
    code_no: Optional[str] = None
    date: Optional[str] = None
    bv_ref_no: Optional[str] = None
    lc_no: Optional[str] = None
    user_id: int
    lc_id: int
    version_bv: int

    class Config:
        from_attributes = True


class BVCreate(BVBase):
    chassis: str
    transaction_id: int


class BVCheck(BaseModel):
    chassis: str


class ConfirmAndRejectBV(BaseModel):
    transaction_id: int


class BVResponse(BVBase):
    id: int
