from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SI(Base):
    __tablename__ = "si"
    id = Column(Integer, primary_key=True, index=True)
    gross_weight = Column(Text)
    measurement = Column(Text)
    port_of_loading = Column(Text)
    port_of_discharge = Column(Text)
    number_of_original_bs = Column(Text)
    no_of_packages = Column(Text)
    seal_no = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="si")
