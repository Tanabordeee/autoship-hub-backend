from sqlalchemy import Column, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class VehicleRegister(Base):
    __tablename__ = "vehicle_register"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    model_year = Column(Text)
    seat = Column(Text)
    characteristics = Column(Text)
    car_engine = Column(Text)
    chassis_no = Column(Text)
    colour = Column(Text)
    total_weight = Column(Text)
    vehicle_weight = Column(Text)
    date_of_registration = Column(Text)
    type_car = Column(Text)
    registration_no = Column(Text)
    engine_no = Column(Text)
    vehicle_make = Column(Text)
    province = Column(Text)
    model = Column(Text)
    fuel_type = Column(Text)
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"), nullable=True)
    lc_id = Column(BigInteger, ForeignKey("lc.id"), nullable=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    # Relationships
    lc = relationship("LC", back_populates="vehicle_registers")
    user = relationship("User", back_populates="vehicle_registers")
    pi_items = relationship("PiItem", back_populates="vehicle_register")
    transaction = relationship("Transaction", back_populates="vehicle_registers")
