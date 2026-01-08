from sqlalchemy.orm import Session
from app.models.proforma_invoice import ProformaInvoice
from app.models.proforma_invoice import PiItem
from app.schemas.proforma_invoice import CreateProformaInvoice
class ProformaInvoiceRepo:
    def get_by_id(db:Session, pi_id:int):
        return db.query(ProformaInvoice).filter(ProformaInvoice.id == pi_id).first()
    def create(db:Session, payload:CreateProformaInvoice , user_id:int):
        pi = ProformaInvoice(
            pi_id = payload.pi_id,
            date = payload.date,
            shipper = payload.shipper,
            consignee_name = payload.consignee_name,
            notify_party_name = payload.notify_party_name,
            port_of_loading = payload.port_of_loading,
            port_of_discharge = payload.port_of_discharge,
            payment_term = payload.payment_term,
            term_condition = payload.term_condition,
            bank = payload.bank,
            account_number = payload.account_number,
            swift_code = payload.swift_code,
            total_price = payload.total_price,
            pi_approver = payload.pi_approver,
            user_id = user_id
        )
        db.add(pi)
        db.flush()
        pi_items = []
        for item in payload.items:
            pi_item = PiItem(
                description = item.description,
                item_no = item.item_no,
                unit = item.unit,
                unit_price = item.unit_price,
                amount_in_usd = item.amount_in_usd,
                pi_id = pi.id,
                parent_items = item.parent_items
            )
            pi_items.append(pi_item)
        db.add_all(pi_items)
        db.commit()
        db.refresh(pi)
        return pi