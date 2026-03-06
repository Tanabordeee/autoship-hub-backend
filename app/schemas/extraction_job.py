from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime


class ExtractionJobBase(BaseModel):
    transaction_id: Optional[int] = None
    user_id: int
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None


class ExtractionJobCreate(ExtractionJobBase):
    id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ExtractionJobUpdate(BaseModel):
    status: Optional[str] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ExtractionJob(ExtractionJobBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
