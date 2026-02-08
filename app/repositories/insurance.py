from sqlalchemy.orm import Session
from app.schemas.insurance import InsuranceCreate
from app.models.insurance import Insurance


class InsuranceRepo:
    def create(db: Session, payload: InsuranceCreate, user_id: int):
        insurance = Insurance(
            name=payload.name,
            certificate_no=payload.certificate_no,
            name_of_insured=payload.name_of_insured,
            vessel=payload.vessel,
            sailing_on_or_about=payload.sailing_on_or_about,
            voyage=payload.voyage,
            subject_matter_insured=payload.subject_matter_insured,
            additional_conditional=payload.additional_conditional,
            special_condition_and_warranties=payload.special_condition_and_warranties,
            invoice_no=payload.invoice_no,
            chassis_no=payload.chassis_no,
            engine=payload.engine,
            the_letter_of_credit_number=payload.the_letter_of_credit_number,
            date_of_issue=payload.date_of_issue,
            bank=payload.bank,
            commercial_invoice_no=payload.commercial_invoice_no,
            date=payload.date,
            version_insurance=payload.version_insurance,
            user_id=user_id,
        )
        db.add(insurance)
        db.commit()
        db.refresh(insurance)
        return insurance

    def get_latest_version_by_certificate_no(db: Session, certificate_no: str):
        return (
            db.query(Insurance)
            .filter(Insurance.certificate_no == certificate_no)
            .order_by(Insurance.version_insurance.desc())
            .first()
        )
