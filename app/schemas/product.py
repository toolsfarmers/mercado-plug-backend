import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.product import ProductStatus, ProductType, StockStatus


class SortBy(str, enum.Enum):
    newest = "newest"
    price_asc = "price_asc"
    price_desc = "price_desc"
    most_interacted = "most_interacted"


class ProductCreate(BaseModel):
    store_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    currency: str = "DOP"
    category: Optional[str] = None
    type: ProductType = ProductType.product
    images: list[str] = []
    stock_status: StockStatus = StockStatus.available
    delivery: bool = False

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre del producto no puede estar vacío")
        return v

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("images")
    @classmethod
    def images_max(cls, v: list[str]) -> list[str]:
        if len(v) > 10:
            raise ValueError("Se permiten máximo 10 imágenes por producto")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    type: Optional[ProductType] = None
    images: Optional[list[str]] = None
    stock_status: Optional[StockStatus] = None
    whatsapp_number: Optional[str] = None
    status: Optional[ProductStatus] = None
    delivery: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("El precio no puede ser negativo")
        return v

    @field_validator("images")
    @classmethod
    def images_max(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is not None and len(v) > 10:
            raise ValueError("Se permiten máximo 10 imágenes por producto")
        return v


class ProductResponse(BaseModel):
    id: int
    store_id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    currency: str
    category: Optional[str] = None
    type: ProductType
    images: list[str]
    stock_status: StockStatus
    whatsapp_number: Optional[str] = None
    location_id: Optional[int] = None
    status: ProductStatus
    delivery: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    total: int
    products: list[ProductResponse]


class FeedResponse(BaseModel):
    feed_type: str
    total: int
    products: list[ProductResponse]
