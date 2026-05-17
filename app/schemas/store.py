import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.store import StoreStatus


def _generate_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[áàäâ]", "a", slug)
    slug = re.sub(r"[éèëê]", "e", slug)
    slug = re.sub(r"[íìïî]", "i", slug)
    slug = re.sub(r"[óòöô]", "o", slug)
    slug = re.sub(r"[úùüû]", "u", slug)
    slug = re.sub(r"[ñ]", "n", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


class StoreCreate(BaseModel):
    seller_id: int
    store_name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    whatsapp_number: Optional[str] = None

    @field_validator("store_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre de la tienda no puede estar vacío")
        return v

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(
                "El slug solo puede contener letras minúsculas, números y guiones (ej: mi-tienda)"
            )
        return v

    def resolve_slug(self) -> str:
        return self.slug if self.slug else _generate_slug(self.store_name)


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    commission_rate: Optional[Decimal] = Field(None, ge=Decimal("0"), le=Decimal("1"))
    status: Optional[StoreStatus] = None

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", v):
            raise ValueError(
                "El slug solo puede contener letras minúsculas, números y guiones"
            )
        return v


class StoreResponse(BaseModel):
    id: int
    seller_id: int
    store_name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    location_id: Optional[int] = None
    commission_rate: Decimal
    status: StoreStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreListResponse(BaseModel):
    total: int
    stores: list[StoreResponse]
