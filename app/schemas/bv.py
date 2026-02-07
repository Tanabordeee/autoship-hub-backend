from pydantic import BaseModel


class BVCreate(BaseModel):
    type_of_vehicle: str
    make: str
    model: str
    seat: str
    commonly_called: str
    manufacture_grade: str
    body_colour: str
    fuel_type: str
    year_of_manufacture: str
    inspection_mileage: str
    engine_capacity: str
    engine_no: str
    driving_system: str
    marks_of_accident_on_chassis: str
    condition_of_chassis: str
    country_of_origin: str
    year_month_of_first_registration: str
    code_no: str
    date: str
    bv_ref_no: str
    lc_no: str
    user_id: int
    lc_id: int
    chassis: str
    version_bv: int
    transaction_id: int


class BVCheck(BaseModel):
    chassis: str


class ConfirmAndRejectBV(BaseModel):
    transaction_id: int
