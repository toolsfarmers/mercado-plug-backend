import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CommissionStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"


class Commission(Base):
    __tablename__ = "commissions"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(
        Integer,
        ForeignKey("sales.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount = Column(Numeric(12, 2), nullable=False)
    rate = Column(Numeric(5, 4), nullable=False)
    status = Column(
        Enum(CommissionStatus), nullable=False, default=CommissionStatus.pending, index=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sale = relationship("Sale", backref="commission", uselist=False)
    store = relationship("Store", backref="commissions")


class CommissionPayment(Base):
    __tablename__ = "commission_payments"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount_paid = Column(Numeric(12, 2), nullable=False)
    commissions_count = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    settled_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    store = relationship("Store", backref="commission_payments")
    settler = relationship("User", backref="commission_payments")
