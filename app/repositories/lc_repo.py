from sqlalchemy.orm import Session
from app.models.lc import LC
from app.models.proforma_invoice import ProformaInvoice
from app.schemas.lc import LCBase
class LCRepo:
    def get_latest_version_by_lc_no(db:Session, lc_no:str):
        """Get the latest version of LC by lc_no"""
        return db.query(LC).filter(LC.lc_no == lc_no).order_by(LC.versions.desc()).first()
    def create(db:Session, payload:LCBase , user_id:int , pi_id:list[int] = []):
        lc = LC(
            beneficiary_59 = payload.beneficiary_59,
            applicant_50 = payload.applicant_50,
            description_of_good_45a_45b = payload.description_of_good_45a_45b,
            versions = payload.versions,
            date_of_issue_31c = payload.date_of_issue_31c,
            lc_no = payload.lc_no,
            document_require_46a = payload.document_require_46a,
            docmentary_credit_number_20 = payload.docmentary_credit_number_20,
            sender_reference_20 = payload.sender_reference_20,
            receiver_reference_21 = payload.receiver_reference_21,
            issuing_bank_reference_23 = payload.issuing_bank_reference_23,
            issuing_bank_52a = payload.issuing_bank_52a,
            port_of_loading_of_departure_44e = payload.port_of_loading_of_departure_44e,
            number_of_amendment_26e = payload.number_of_amendment_26e,
            date_of_amendment_30 = payload.date_of_amendment_30,
            purpose_of_message_22a = payload.purpose_of_message_22a,
            sequence_of_total_27 = payload.sequence_of_total_27,
            form_of_documentary_credit_40a = payload.form_of_documentary_credit_40a,
            applicable_rules_40e = payload.applicable_rules_40e,
            date_and_place_of_expiry_31d = payload.date_and_place_of_expiry_31d,
            currency_code_32b = payload.currency_code_32b,
            available_with_41d = payload.available_with_41d,
            partial_shipments_43p = payload.partial_shipments_43p,
            transhipment_43t = payload.transhipment_43t,
            port_of_discharge_44f = payload.port_of_discharge_44f,
            latest_date_of_shipment_44c = payload.latest_date_of_shipment_44c,
            charges_71d = payload.charges_71d,
            additional_conditions_47a = payload.additional_conditions_47a,
            period_for_presentation_in_days_48 = payload.period_for_presentation_in_days_48,
            confirmation_instructions_49 = payload.confirmation_instructions_49,
            instructions_to_the_paying_accepting_negotiating_bank_78 = payload.instructions_to_the_paying_accepting_negotiating_bank_78,
            applicant_bank_51d = payload.applicant_bank_51d,
            drafts_at_42c = payload.drafts_at_42c,
            drawee_42a = payload.drawee_42a,
            pdf_path = payload.pdf_path,
            user_id = user_id
        )
        db.add(lc)
        db.commit()
        db.refresh(lc)
        for id_pi in pi_id:
            pi = db.query(ProformaInvoice).filter(ProformaInvoice.id == id_pi).first()
            pi.lc_id = lc.id
            db.commit()
        return lc
    def get_by_id(db:Session , id:int):
        return db.query(LC).filter(LC.id == id).first()