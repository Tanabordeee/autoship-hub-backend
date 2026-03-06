from pydantic import BaseModel, ConfigDict


class CommercialInvoice(BaseModel):
    lc_id: int
    pi_id: int
    si_id: int
    bv_id: int
    booking_id: int
    transaction_id: int
    director: str
    bank: str
    chassis_no: str


class CreateCommercialInvoicePayload(BaseModel):
    transaction_id: int
    director: str
    bank: str
    chassis_no: str


class CommercialInvoiceResponse(BaseModel):
    id: int
    bank: str
    director: str
    user_id: int
    model_config = ConfigDict(from_attributes=True)
