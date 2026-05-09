import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ProductType(str, enum.Enum):
    product = "product"
    service = "service"


class StockStatus(str, enum.Enum):
    available = "available"
    unavailable = "unavailable"


class ProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(
        Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="DOP")
    category = Column(String(100), nullable=True, index=True)
    type = Column(Enum(ProductType), nullable=False, default=ProductType.product)
    images = Column(JSON, nullable=False, default=list)
    stock_status = Column(Enum(StockStatus), nullable=False, default=StockStatus.available)
    location_id = Column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(Enum(ProductStatus), nullable=False, default=ProductStatus.active)
    delivery = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    store = relationship("Store", backref="products")
    location = relationship("Location", backref="products")
