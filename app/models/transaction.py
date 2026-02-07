from sqlalchemy import Column, Integer, Text, ForeignKey
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

    # Singular Relationships (Transaction holds the FK)
    lc = relationship("LC", back_populates="transactions")
    si = relationship("SI", back_populates="transactions")
    bl = relationship("BL", back_populates="transactions")
    insurance = relationship("Insurance", back_populates="transactions")

    proforma_invoices = relationship(
        "ProformaInvoice", back_populates="transaction", cascade="all, delete-orphan"
    )
    bookings = relationship(
        "Booking", back_populates="transaction", cascade="all, delete-orphan"
    )
    vehicle_registers = relationship(
        "VehicleRegister", back_populates="transaction", cascade="all, delete-orphan"
    )
    bvs = relationship("BV", back_populates="transaction", cascade="all, delete-orphan")
