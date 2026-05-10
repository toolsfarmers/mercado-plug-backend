import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InteractionAction(str, enum.Enum):
    click_buy_product = "click_buy_product"
    view_product = "view_product"
    view_store = "view_store"
    share_product = "share_product"


class ProductInteraction(Base):
    __tablename__ = "product_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    store_id = Column(
        Integer,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action = Column(
        Enum(InteractionAction),
        nullable=False,
        default=InteractionAction.click_buy_product,
    )
    date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    user = relationship("User", backref="interactions")
    product = relationship("Product", backref="interactions")
    store = relationship("Store", backref="interactions")
