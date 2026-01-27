from app.db.base_class import Base
from sqlalchemy import Column, Text, BigInteger
from sqlalchemy.orm import relationship


class Customer(Base):
    __tablename__ = "customers"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    customer_name = Column(Text, nullable=False)
    customer_location = Column(Text, nullable=False)
    proforma_invoices = relationship(
        "ProformaInvoice", back_populates="customer", cascade="all, delete-orphan"
    )
