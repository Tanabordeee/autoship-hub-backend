from pydantic import BaseModel


class VehicleRegisterCreate(BaseModel):
    model_year: str
    seat: str
    characteristics: str
    car_engine: str
    chassis_no: str
    colour: str
    total_weight: str
    vehicle_weight: str
    date_of_registration: str
    type_car: str
    registration_no: str
    engine_no: str
    vehicle_make: str
    province: str
    model: str
    fuel_type: str
    lc_id: int
    chassis: str
    transaction_id: int


class VehicleRegisterCreateResponse(BaseModel):
    id: int
