from pydantic import BaseModel


class SICreate(BaseModel):
    gross_weight: str
    measurement: str
    port_of_loading: str
    port_of_discharge: str
    number_of_original_bs: str
    no_of_packages: str
    user_id: int
    pi_id: int
    lc_id: int
    vehicle_register_id: int
    booking_id: int
    output_path: str
    transaction_id: int


class ConfirmSi(BaseModel):
    transaction_id: int
