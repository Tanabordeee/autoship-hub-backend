from pydantic import BaseModel


class BLCheck(BaseModel):
    lc_id: int
    booking_id: int
    vehicle_register_id: int
    pi_id: int
    si_id: int
