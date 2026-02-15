from pydantic import BaseModel


class BencerGenerate(BaseModel):
    lc_id: int
    vehicle_register_id: int
    transaction_id: int
    date: str
    director: str
    commercial_invoice_id: int


class CreateBencer(BaseModel):
    date: str
    director: str
    transaction_id: int
