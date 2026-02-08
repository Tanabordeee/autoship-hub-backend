from pydantic import BaseModel


class InsuranceCheck(BaseModel):
    lc_id: int
    pi_id: int
    vr_id: int
    booking_id: int
    bl_id: int


class InsuranceCreate(BaseModel):
    name: str
    version_insurance: int
    vessel: str
    name_of_insured: str
    sailing_on_or_about: str
    voyage: str
    certificate_no: str
    additional_conditional: str
    special_condition_and_warranties: str
    subject_matter_insured: str
    invoice_no: str
    chassis_no: str
    engine: str
    the_letter_of_credit_number: str
    date_of_issue: str
    bank: str
    commercial_invoice_no: str
    date: str


class InsuranceConfirm(BaseModel):
    insurance_id: int
    transaction_id: int
