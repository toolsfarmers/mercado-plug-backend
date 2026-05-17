from typing import Optional

from pydantic import BaseModel, field_validator


class LocationCreate(BaseModel):
    country: str = "República Dominicana"
    province: str
    municipality: Optional[str] = None
    sector: Optional[str] = None
    address_line: Optional[str] = None
    reference_point: Optional[str] = None
    additional_details: Optional[str] = None

    @field_validator("province")
    @classmethod
    def province_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La provincia no puede estar vacía")
        return v

    @field_validator("country")
    @classmethod
    def country_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El país no puede estar vacío")
        return v


class LocationUpdate(BaseModel):
    country: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None
    sector: Optional[str] = None
    address_line: Optional[str] = None
    reference_point: Optional[str] = None
    additional_details: Optional[str] = None


class LocationResponse(BaseModel):
    id: int
    country: str
    province: str
    municipality: Optional[str] = None
    sector: Optional[str] = None
    address_line: Optional[str] = None
    reference_point: Optional[str] = None
    additional_details: Optional[str] = None

    model_config = {"from_attributes": True}


class LocationListResponse(BaseModel):
    total: int
    locations: list[LocationResponse]


class CountryEntry(BaseModel):
    country: str
    provinces: list[str]


class LocationCatalogResponse(BaseModel):
    countries: list[CountryEntry]
