from sqlalchemy import Column, Integer, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base_class import Base


class LC(Base):
    __tablename__ = "lc"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    beneficiary_59 = Column(Text)
    applicant_50 = Column(Text)
    description_of_good_45a_45b = Column(JSONB)
    versions = Column(Integer)
    date_of_issue_31c = Column(Text)
    lc_no = Column(Text)
    document_require_46a = Column(JSONB)
    docmentary_credit_number_20 = Column(Text)
    sender_reference_20 = Column(Text)
    receiver_reference_21 = Column(Text)
    issuing_bank_reference_23 = Column(Text)
    issuing_bank_52a = Column(Text)
    port_of_loading_of_departure_44e = Column(Text)
    number_of_amendment_26e = Column(Text)
    date_of_amendment_30 = Column(Text)
    purpose_of_message_22a = Column(Text)
    sequence_of_total_27 = Column(Text)
    form_of_documentary_credit_40a = Column(Text)
    applicable_rules_40e = Column(Text)
    date_and_place_of_expiry_31d = Column(Text)
    currency_code_32b = Column(Text)
    available_with_41d = Column(Text)
    partial_shipments_43p = Column(Text)
    transhipment_43t = Column(Text)
    port_of_discharge_44f = Column(Text)
    latest_date_of_shipment_44c = Column(Text)
    charges_71d = Column(Text)
    additional_conditions_47a = Column(Text)
    period_for_presentation_in_days_48 = Column(Text)
    confirmation_instructions_49 = Column(Text)
    instructions_to_the_paying_accepting_negotiating_bank_78 = Column(Text)
    applicant_bank_51d = Column(Text)
    drafts_at_42c = Column(Text)
    drawee_42a = Column(Text)
    pdf_path = Column(Text)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Relationship
    user = relationship("User", back_populates="lcs")
    proforma_invoices = relationship("ProformaInvoice", back_populates="lc")
    bookings = relationship("Booking", back_populates="lc")
    vehicle_registers = relationship("VehicleRegister", back_populates="lc")
