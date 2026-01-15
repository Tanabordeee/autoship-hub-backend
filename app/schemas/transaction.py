from pydantic import BaseModel
from typing import List

class TransactionCreate(BaseModel):
    status: str
    current_process: str

class TransactionUpdate(BaseModel):
    status: str
    current_process: str