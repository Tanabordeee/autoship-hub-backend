from app.db.base_class import Base
from sqlalchemy import Column, Text, BigInteger, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class BL(Base):
    __tablename__ = "bl"
    id = Column(BigInteger, primary_key=True, index=True)
    version_bl = Column(Integer)
    bl_number = Column(Text)
    jo_number = Column(Text)
    shipper = Column(Text)
    consignee = Column(Text)
    notify_party = Column(Text)
    place_of_receipt = Column(Text)
    port_of_loading = Column(Text)
    port_of_discharge = Column(Text)
    ocean_vessel = Column(Text)
    place_of_delivery = Column(Text)
    freight_payable_at = Column(Text)
    number_of_original_bs = Column(Text)
    gross_weight = Column(Text)
    measurement = Column(Text)
    cy_cf = Column(Text)
    description_of_good = Column(Text)
    container = Column(Text)
    seal_no = Column(Text)
    size_no = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="bls")
