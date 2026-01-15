from sqlalchemy.orm import Session, joinedload
from app.models.proforma_invoice import ProformaInvoice
from app.models.proforma_invoice import PiItem
from app.models.transaction import Transaction
from app.schemas.proforma_invoice import CreateProformaInvoice
from app.models.customer import Customer
from app.repositories.transaction_repo import TransactionRepo
from app.schemas.transaction import TransactionCreate
class ProformaInvoiceRepo:
    def get_by_id(db:Session, pi_id:str):
        return db.query(ProformaInvoice).options(joinedload(ProformaInvoice.transaction)).filter(ProformaInvoice.pi_id == pi_id).first()
    def get_all(db:Session):
        rows = db.query(
        ProformaInvoice.pi_id,
        ProformaInvoice.date,
        Customer.customer_name,
        Customer.customer_location,
        ProformaInvoice.total_price,
        Transaction.status,
        Transaction.id
        )\
        .join(Customer)\
        .join(Transaction)\
        .all()

        return [
            {
                "invoice_id": r.pi_id,
                "date": r.date,
                "customer": r.customer_name,
                "location": r.customer_location,
                "total": float(r.total_price),
                "status": r.status,
                "transaction_id":r.id
            }
            for r in rows
        ]

    def create(db:Session, payload:CreateProformaInvoice , user_id:int):
        transaction = TransactionRepo.create(db, TransactionCreate(status="pending", current_process="proforma_invoice"))
        lines = [line.strip() for line in payload.consignee_name.splitlines()]
        customer = Customer(
            customer_name = lines[0] if lines else "",
            customer_location = "\n".join(lines[1:]) if len(lines) > 1 else ""
        )
        db.add(customer)
        db.flush()

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
            user_id = user_id,
            transaction_id = transaction.id,
            customer_id = customer.id
        )
        db.add(pi)
        db.flush()
        item_map = {}
        # First pass: Create all items
        for item_data in payload.items:
            pi_item = PiItem(
                description = item_data.description,
                item_no = item_data.item_no,
                unit = item_data.unit,
                unit_price = item_data.unit_price,
                amount_in_usd = item_data.amount_in_usd,
                pi_id = pi.id
            )
            item_map[item_data.item_no] = pi_item

        # Second pass: Link parents and add to session
        for item_data in payload.items:
            if item_data.parent_items:
                parent_item = item_map.get(item_data.parent_items)
                if parent_item:
                    item_map[item_data.item_no].parent = parent_item
            db.add(item_map[item_data.item_no])

        db.commit()
        db.refresh(pi)
        return pi
    def update_pi_status(db:Session , pi_id:str , status:str, approver:str=None):
        pi = db.query(ProformaInvoice).filter(ProformaInvoice.pi_id == pi_id).first()
        if not pi:
            raise BaseException("Proforma Invoice not found")
        if approver :
            pi.pi_approver = approver
        pi.transaction.status = status
        db.commit()
        db.refresh(pi)  
        db.refresh(pi.transaction)
        return pi