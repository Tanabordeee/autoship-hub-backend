from pydantic import BaseModel
from typing import Optional


class TransactionCreate(BaseModel):
    status: str
    current_process: str


class TransactionUpdate(BaseModel):
    status: str
    current_process: str
    lc_id: Optional[int] = None
    si_id: Optional[int] = None
    bl_id: Optional[int] = None
