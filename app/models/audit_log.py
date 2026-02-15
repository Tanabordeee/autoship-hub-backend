from sqlalchemy import Column, BigInteger, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(BigInteger, primary_key=True, index=True)
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    action_type = Column(Text)
    entity_type = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"))

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    transaction = relationship("Transaction", back_populates="audit_logs")
