from pydantic import BaseModel


class TransactionCreate(BaseModel):
    status: str
    current_process: str


class TransactionUpdate(BaseModel):
    status: str
    current_process: str
