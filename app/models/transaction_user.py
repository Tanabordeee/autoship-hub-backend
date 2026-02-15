from sqlalchemy import Column, ForeignKey, BigInteger, Table
from app.db.base_class import Base

transaction_users = Table(
    "transaction_users",
    Base.metadata,
    Column(
        "transaction_id",
        BigInteger,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
