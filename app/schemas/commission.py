from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.commission import CommissionStatus


class CommissionResponse(BaseModel):
    id: int
    sale_id: int
    store_id: Optional[int] = None
    amount: Decimal
    rate: Decimal
    status: CommissionStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class CommissionListResponse(BaseModel):
    total: int
    commissions: list[CommissionResponse]


class CommissionPaymentResponse(BaseModel):
    id: int
    store_id: Optional[int] = None
    amount_paid: Decimal
    commissions_count: int
    notes: Optional[str] = None
    settled_by: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommissionPaymentListResponse(BaseModel):
    total: int
    payments: list[CommissionPaymentResponse]


class StoreBalanceResponse(BaseModel):
    store_id: int
    store_name: str
    commission_rate: Decimal
    pending_count: int
    pending_amount: Decimal
    currency: str = "DOP"


class CommissionSummaryItem(BaseModel):
    store_id: int
    store_name: str
    commission_rate: Decimal
    pending_count: int
    pending_amount: Decimal


class CommissionSummaryResponse(BaseModel):
    total_stores_with_debt: int
    total_pending_amount: Decimal
    stores: list[CommissionSummaryItem]


class SettleRequest(BaseModel):
    notes: Optional[str] = None
