from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class LCBase(BaseModel):
    beneficiary_59: Optional[str] = None
    applicant_50: Optional[str] = None
    description_of_good_45a_45b: Optional[Any] = None
    versions: Optional[int] = None
    date_of_issue_31c: Optional[str] = None
    lc_no: Optional[str] = None
    document_require_46a: Optional[Any] = None
    docmentary_credit_number_20: Optional[str] = None
    sender_reference_20: Optional[str] = None
    receiver_reference_21: Optional[str] = None
    issuing_bank_reference_23: Optional[str] = None
    issuing_bank_52a: Optional[str] = None
    port_of_loading_of_departure_44e: Optional[str] = None
    number_of_amendment_26e: Optional[str] = None
    date_of_amendment_30: Optional[str] = None
    purpose_of_message_22a: Optional[str] = None
    sequence_of_total_27: Optional[str] = None
    form_of_documentary_credit_40a: Optional[str] = None
    applicable_rules_40e: Optional[str] = None
    date_and_place_of_expiry_31d: Optional[str] = None
    currency_code_32b: Optional[str] = None
    available_with_41d: Optional[str] = None
    partial_shipments_43p: Optional[str] = None
    transhipment_43t: Optional[str] = None
    port_of_discharge_44f: Optional[str] = None
    latest_date_of_shipment_44c: Optional[str] = None
    charges_71d: Optional[str] = None
    additional_conditions_47a: Optional[str] = None
    period_for_presentation_in_days_48: Optional[str] = None
    confirmation_instructions_49: Optional[str] = None
    instructions_to_the_paying_accepting_negotiating_bank_78: Optional[str] = None
    applicant_bank_51d: Optional[str] = None
    drafts_at_42c: Optional[str] = None
    drawee_42a: Optional[str] = None
    pdf_path: Optional[str] = None
    user_id: Optional[int] = None

class LCCreate(LCBase):
    pass

class LCUpdate(LCBase):
    pass

class LC(LCBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True