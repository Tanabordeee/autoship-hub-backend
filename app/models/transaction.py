from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, BigInteger, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Text, nullable=False)
    current_process = Column(Text, nullable=False)
    proforma_invoices = relationship("ProformaInvoice", back_populates="transaction", cascade="all, delete-orphan")
    