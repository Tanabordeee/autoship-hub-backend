from app.db.base import Base
from sqlalchemy import Column, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Booking(Base):
    __tablename__ = "booking"
    id = Column(BigInteger, primary_key=True, index=True)
    at_before = Column(Text)
    booking_no = Column(Text)
    date = Column(Text)
    cut_off_vgm = Column(Text)
    cut_off_si = Column(Text)
    booking_name = Column(Text)
    etd = Column(Text)
    fob_at = Column(Text)
    quantity = Column(Text)
    consignee = Column(Text)
    return_date = Column(Text)
    cy_date = Column(Text)
    cy_at = Column(Text)
    carrier = Column(Text)
    closing_date = Column(Text)
    port_of_disch = Column(Text)
    shipper = Column(Text)
    port_of_del = Column(Text)
    return_yard = Column(Text)
    port_of_loading = Column(Text)
    eta_dest = Column(Text)
    feeder = Column(Text)
    place_of_rec = Column(Text)
    paperless_code = Column(Text)
    carrier_booking_no = Column(Text)
    # ฝั่งที่มี FK
    user_id = Column(BigInteger, ForeignKey("users.id"))
    user = relationship("User", back_populates="bookings")
    lc_id = Column(BigInteger, ForeignKey("lc.id"))
    lc = relationship("LC", back_populates="bookings")
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"))
    transaction = relationship("Transaction", back_populates="bookings")
