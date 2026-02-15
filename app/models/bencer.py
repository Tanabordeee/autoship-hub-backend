from sqlalchemy import Column, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Bencer(Base):
    __tablename__ = "bencer"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    date = Column(Text, nullable=False)
    director = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"))

    user = relationship("User", back_populates="bencers")
    transactions = relationship("Transaction", back_populates="bencer")
