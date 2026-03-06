from sqlalchemy import Column, String, DateTime, ForeignKey, Text, BigInteger, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from app.db.base_class import Base


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    status = Column(
        String, nullable=False, default="pending"
    )  # pending, processing, completed, failed
    result = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )
