from sqlalchemy import Column, BigInteger, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Insurance(Base):
    __tablename__ = "insurance"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(Text)
    version_insurance = Column(Integer)
    vessel = Column(Text)
    name_of_insured = Column(Text)
    sailing_on_or_about = Column(Text)
    voyage = Column(Text)
    certificate_no = Column(Text)
    additional_conditional = Column(Text)
    special_condition_and_warranties = Column(Text)
    subject_matter_insured = Column(Text)
    invoice_no = Column(Text)
    chassis_no = Column(Text)
    engine = Column(Text)
    the_letter_of_credit_number = Column(Text)
    date_of_issue = Column(Text)
    bank = Column(Text)
    commercial_invoice_no = Column(Text)
    date = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"))

    # Relationships
    user = relationship("User", back_populates="insurances")
    transactions = relationship("Transaction", back_populates="insurance")
