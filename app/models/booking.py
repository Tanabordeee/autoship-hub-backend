from app.db.base_class import Base
from sqlalchemy import Column, Text, BigInteger, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Booking(Base):
    __tablename__ = "booking"

    id = Column(BigInteger, primary_key=True, index=True)
    at_before = Column(Text)
    booking_no = Column(Text)
    date = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    cut_off_vgm = Column(Text)
    cut_off_si = Column(Text)
    booking_name = Column(Text)
    etd = Column(Text)
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
    create_at = Column(DateTime(timezone=True), server_default=func.now())
    lc_id = Column(BigInteger, ForeignKey("lc.id"))
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"))
    fob_at = Column(Text)
    quantity = Column(Text)
    carrier_booking_no = Column(Text)

    # Relationships
    user = relationship("User", back_populates="bookings")
    lc = relationship("LC", back_populates="bookings")
    transaction = relationship("Transaction", back_populates="bookings")
