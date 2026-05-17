from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    seller_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="DOP")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    order = relationship("Order", backref="sale", uselist=False)
    store = relationship("Store", backref="sales")
    product = relationship("Product", backref="sales")
    seller = relationship("User", backref="sales")
