from sqlalchemy.orm import Session
from app.models.lc import LC
from app.models.proforma_invoice import ProformaInvoice
from app.schemas.lc import LCBase


class LCRepo:
    def get_latest_version_by_lc_no(db: Session, lc_no: str):
        """Get the latest version of LC by lc_no"""
        return (
            db.query(LC).filter(LC.lc_no == lc_no).order_by(LC.versions.desc()).first()
        )

    def create(db: Session, payload: LCBase, user_id: int, pi_id: list[int] = []):
        LC_FIELDS = [
            "beneficiary_59",
            "applicant_50",
            "description_of_good_45a_45b",
            "versions",
            "date_of_issue_31c",
            "lc_no",
            "document_require_46a",
            "docmentary_credit_number_20",
            "sender_reference_20",
            "receiver_reference_21",
            "issuing_bank_reference_23",
            "issuing_bank_52a",
            "port_of_loading_of_departure_44e",
            "number_of_amendment_26e",
            "date_of_amendment_30",
            "purpose_of_message_22a",
            "sequence_of_total_27",
            "form_of_documentary_credit_40a",
            "applicable_rules_40e",
            "date_and_place_of_expiry_31d",
            "currency_code_32b",
            "available_with_41d",
            "partial_shipments_43p",
            "transhipment_43t",
            "port_of_discharge_44f",
            "latest_date_of_shipment_44c",
            "charges_71d",
            "additional_conditions_47a",
            "period_for_presentation_in_days_48",
            "confirmation_instructions_49",
            "instructions_to_the_paying_accepting_negotiating_bank_78",
            "applicant_bank_51d",
            "drafts_at_42c",
            "drawee_42a",
            "pdf_path",
        ]

        def merge_lc_data(payload, back_lc, fields: list[str]):
            data = {}
            for field in fields:
                new_value = getattr(payload, field)
                if new_value is not None:
                    data[field] = new_value
                else:
                    data[field] = getattr(back_lc, field) if back_lc else None
            return data

        back_lc = None
        if payload.versions > 1:
            back_lc = (
                db.query(LC)
                .filter(LC.lc_no == payload.lc_no)
                .order_by(LC.versions.desc())
                .first()
            )

        lc_data = merge_lc_data(payload, back_lc, LC_FIELDS)
        lc_data["user_id"] = user_id

        lc = LC(**lc_data)

        db.add(lc)
        db.commit()
        db.refresh(lc)

        for id_pi in pi_id:
            pi = db.query(ProformaInvoice).filter(ProformaInvoice.id == id_pi).first()
            pi.lc_id = lc.id

        db.commit()
        return lc

    def get_by_id(db: Session, id: int):
        return db.query(LC).filter(LC.id == id).first()

    def get_all_lc_no(db: Session):
        results = db.query(LC.lc_no).distinct().all()
        return [r[0] for r in results]
