from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, description="Cantidad del producto")
    delivery_address: Optional[str] = None
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_id: Optional[int] = None
    store_id: Optional[int] = None
    quantity: int
    unit_price: Decimal
    currency: str
    status: OrderStatus
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    total: int
    orders: list[OrderResponse]
