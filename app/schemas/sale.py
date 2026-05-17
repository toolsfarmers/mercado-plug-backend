from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SaleResponse(BaseModel):
    id: int
    order_id: int
    store_id: Optional[int] = None
    product_id: Optional[int] = None
    seller_id: Optional[int] = None
    amount: Decimal
    currency: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleListResponse(BaseModel):
    total: int
    sales: list[SaleResponse]
