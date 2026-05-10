from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.interaction import InteractionAction


# ── Registro de interacción ────────────────────────────────────────────────────

class InteractionCreate(BaseModel):
    product_id: int
    user_id: Optional[int] = None
    action: InteractionAction = InteractionAction.click_buy_product


class InteractionResponse(BaseModel):
    id: int
    product_id: int
    store_id: int
    user_id: Optional[int] = None
    action: InteractionAction
    date: datetime

    model_config = {"from_attributes": True}


# ── Stats por tienda (seller) ──────────────────────────────────────────────────

class ProductStat(BaseModel):
    product_id: int
    product_name: str
    count: int


class DailyStat(BaseModel):
    date: str
    count: int


class ActionStat(BaseModel):
    action: InteractionAction
    count: int


class SellerStatsResponse(BaseModel):
    store_id: int
    total_interactions: int
    by_product: list[ProductStat]
    by_action: list[ActionStat]
    by_date: list[DailyStat]


# ── Stats globales (admin) ─────────────────────────────────────────────────────

class StoreStat(BaseModel):
    store_id: int
    store_name: str
    count: int


class AdminStatsResponse(BaseModel):
    total_interactions: int
    by_store: list[StoreStat]
    by_action: list[ActionStat]
    by_date: list[DailyStat]


# ── User interests ─────────────────────────────────────────────────────────────

class CategoryInterest(BaseModel):
    category: str
    click_count: int


class UserInterestsResponse(BaseModel):
    user_id: int
    top_categories: list[CategoryInterest]
