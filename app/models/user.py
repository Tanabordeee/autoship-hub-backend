from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    name = Column(String, nullable=False)
    proforma_invoices = relationship("ProformaInvoice", back_populates="user")
    lcs = relationship("LC", back_populates="user", lazy="dynamic")
    # ฝั่งแม่ของ booking
    bookings = relationship("Booking", back_populates="user")
    vehicle_registers = relationship("VehicleRegister", back_populates="user")
    si = relationship("SI", back_populates="user")
    bls = relationship("BL", back_populates="user")
    bvs = relationship("BV", back_populates="user")
    insurances = relationship("Insurance", back_populates="user")
