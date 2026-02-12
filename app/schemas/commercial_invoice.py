from pydantic import BaseModel


class CommercialInvoice(BaseModel):
    lc_id: int
    pi_id: int
    si_id: int
    bv_id: int
    booking_id: int
    transaction_id: int
    director: str
    bank: str


class CreateCommercialInvoicePayload(BaseModel):
    transaction_id: int
    director: str
    bank: str


class CommercialInvoiceResponse(BaseModel):
    id: int
    bank: str
    director: str
    user_id: int

    class Config:
        from_attributes = True
