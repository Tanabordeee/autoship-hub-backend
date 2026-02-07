from pydantic import BaseModel


class InsuranceCheck(BaseModel):
    lc_id: int
    pi_id: int
    vr_id: int
    booking_id: int
    bl_id: int
