from app.db.base_class import Base
from sqlalchemy import Column, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship


class CommercialInvoice(Base):
    __tablename__ = "commercial_invoice"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    bank = Column(Text, nullable=False)
    director = Column(Text, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="commercial_invoice")
    transactions = relationship("Transaction", back_populates="commercial_invoice")
