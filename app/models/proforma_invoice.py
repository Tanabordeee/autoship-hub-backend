from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    BigInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class ProformaInvoice(Base):
    __tablename__ = "proforma_invoice"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pi_id = Column(Text, nullable=False)
    date = Column(Text, nullable=False)

    shipper = Column(Text, nullable=False)
    consignee_name = Column(Text, nullable=False)
    notify_party_name = Column(Text, nullable=False)

    port_of_loading = Column(Text, nullable=False)
    port_of_discharge = Column(Text, nullable=False)

    payment_term = Column(Text, nullable=False)
    term_condition = Column(Text, nullable=False)

    bank = Column(Text, nullable=False)
    account_number = Column(Text, nullable=False)
    swift_code = Column(Text, nullable=False)

    total_price = Column(Numeric(12, 2), nullable=False)

    pi_approver = Column(Text, nullable=False)

    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    transaction_id = Column(
        BigInteger, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    customer_id = Column(
        BigInteger, ForeignKey("customers.id", ondelete="CASCADE"), nullable=True
    )
    lc_id = Column(BigInteger, ForeignKey("lc.id", ondelete="SET NULL"), nullable=True)
    # Relationships
    user = relationship("User", back_populates="proforma_invoices")
    items = relationship(
        "PiItem",
        back_populates="proforma_invoice",
        cascade="all, delete-orphan",
        order_by="PiItem.item_no",
    )
    customer = relationship("Customer", back_populates="proforma_invoices")
    transaction = relationship("Transaction", back_populates="proforma_invoices")
    lc = relationship("LC", back_populates="proforma_invoices")


class PiItem(Base):
    __tablename__ = "pi_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    amount_in_usd = Column(Numeric(12, 2), nullable=False)
    description = Column(Text)
    item_no = Column(Integer)
    unit = Column(Integer)
    pi_id = Column(
        BigInteger,
        ForeignKey("proforma_invoice.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_items = Column(BigInteger, ForeignKey("pi_items.id", ondelete="CASCADE"))
    item_type = Column(Text)
    __table_args__ = (UniqueConstraint("pi_id", "item_no", name="uq_pi_items_item_no"),)

    # Relationships
    proforma_invoice = relationship("ProformaInvoice", back_populates="items")
    parent = relationship("PiItem", remote_side=[id], backref="children")
