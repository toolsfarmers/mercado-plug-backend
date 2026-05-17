import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True
    )
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="DOP")
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending, index=True)
    delivery_address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", backref="orders")
    product = relationship("Product", backref="orders")
    store = relationship("Store", backref="orders")
