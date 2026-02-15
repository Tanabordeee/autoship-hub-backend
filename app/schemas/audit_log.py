from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AuditLogResponse(BaseModel):
    id: int
    create_at: datetime
    action_type: str
    entity_type: str
    user_id: Optional[int]
    user_name: Optional[str]
    transaction_id: int

    class Config:
        from_attributes = True
