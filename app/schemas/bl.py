from pydantic import BaseModel


class BLCheck(BaseModel):
    lc_id: int
    booking_id: int
    vehicle_register_id: int
    pi_id: int
    si_id: int


class BLCreate(BaseModel):
    user_id: int
    bl_number: str
    jo_number: str
    shipper: str
    consignee: str
    notify_party: str
    place_of_receipt: str
    port_of_loading: str
    port_of_discharge: str
    ocean_vessel: str
    place_of_delivery: str
    freight_payable_at: str
    number_of_original_bs: str
    gross_weight: str
    measurement: str
    cy_cf: str
    description_of_good: str
    container: str
    seal_no: str
    size_no: str
    version_bl: int


class TransactionStatusUpdate(BaseModel):
    transaction_id: int
