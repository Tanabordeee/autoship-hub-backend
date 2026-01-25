from pydantic import BaseModel
from typing import List, Optional

class PiItemCreate(BaseModel):
    description:str
    item_no:int
    unit: int
    unit_price: float
    amount_in_usd: float
    parent_items: Optional[int] = None
    item_type : str
    
class CreateProformaInvoice(BaseModel):
    pi_id: str
    date: str

    shipper: str
    consignee_name: str
    notify_party_name: str

    port_of_loading: str
    port_of_discharge: str

    payment_term: str
    term_condition: str

    bank: str
    account_number: str
    swift_code: str

    total_price: float
    pi_approver: str
    items: List[PiItemCreate]  

class ApproveProformaInvoice(BaseModel):
    approver: str

class ChassisRequest(BaseModel):
    pi_id: List[int]