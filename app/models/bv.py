from app.db.base_class import Base
from sqlalchemy import Column, Text, BigInteger, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class BV(Base):
    __tablename__ = "bv"
    id = Column(BigInteger, primary_key=True, index=True)
    type_of_vehicle = Column(Text)
    make = Column(Text)
    model = Column(Text)
    seat = Column(Text)
    commonly_called = Column(Text)
    manufacture_grade = Column(Text)
    body_colour = Column(Text)
    fuel_type = Column(Text)
    year_of_manufacture = Column(Text)
    inspection_mileage = Column(Text)
    engine_capacity = Column(Text)
    engine_no = Column(Text)
    driving_system = Column(Text)
    marks_of_accident_on_chassis = Column(Text)
    condition_of_chassis = Column(Text)
    country_of_origin = Column(Text)
    year_month_of_first_registration = Column(Text)
    code_no = Column(Text)
    date = Column(Text)
    bv_ref_no = Column(Text)
    version_bv = Column(Integer)
    lc_no = Column(Text)
    lc_id = Column(BigInteger, ForeignKey("lc.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="bvs")
    lc = relationship("LC", back_populates="bvs")
    pi_items = relationship("PiItem", back_populates="bv")
