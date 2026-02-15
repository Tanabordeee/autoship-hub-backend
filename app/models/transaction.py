from sqlalchemy import Column, Integer, Text, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Text, nullable=False)
    current_process = Column(Text, nullable=False)
    lc_id = Column(Integer, ForeignKey("lc.id"))
    si_id = Column(Integer, ForeignKey("si.id"))
    bl_id = Column(Integer, ForeignKey("bl.id"))
    insurance_id = Column(Integer, ForeignKey("insurance.id"))
    commercial_invoice_id = Column(Integer, ForeignKey("commercial_invoice.id"))
    bencer_id = Column(Integer, ForeignKey("bencer.id"))
    booking_id = Column(Integer, ForeignKey("booking.id"))
    vehicle_register_id = Column(Integer, ForeignKey("vehicle_register.id"))
    bv_id = Column(Integer, ForeignKey("bv.id"))
    proforma_invoice_id = Column(BigInteger, ForeignKey("proforma_invoice.id"))
    # Singular Relationships (Transaction holds the FK)
    lc = relationship("LC", back_populates="transactions")
    si = relationship("SI", back_populates="transactions")
    bl = relationship("BL", back_populates="transactions")
    bencer = relationship("Bencer", back_populates="transactions")
    commercial_invoice = relationship(
        "CommercialInvoice", back_populates="transactions"
    )
    insurance = relationship("Insurance", back_populates="transactions")
    users = relationship(
        "User", secondary="transaction_users", back_populates="transactions"
    )

    proforma_invoice = relationship(
        "ProformaInvoice", back_populates="transaction", uselist=False
    )
    booking = relationship("Booking", back_populates="transaction", uselist=False)
    vehicle_register = relationship(
        "VehicleRegister", back_populates="transaction", uselist=False
    )
    bv = relationship("BV", back_populates="transaction", uselist=False)
