from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.product import Product, ProductStatus, StockStatus
from app.schemas.location import (
    CountryEntry,
    LocationCatalogResponse,
    LocationCreate,
    LocationListResponse,
    LocationResponse,
    LocationUpdate,
)

router = APIRouter()


def _get_location_or_404(location_id: int, db: Session) -> Location:
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ubicación no encontrada",
        )
    return location


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)):
    location = Location(**payload.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.get("/", response_model=LocationListResponse)
def list_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    province: str | None = Query(None, description="Filtrar por provincia"),
    municipality: str | None = Query(None, description="Filtrar por municipio"),
    db: Session = Depends(get_db),
):
    query = db.query(Location)
    if province:
        query = query.filter(Location.province.ilike(f"%{province}%"))
    if municipality:
        query = query.filter(Location.municipality.ilike(f"%{municipality}%"))
    total = query.count()
    locations = query.offset(skip).limit(limit).all()
    return {"total": total, "locations": locations}


@router.get("/catalog", response_model=LocationCatalogResponse)
def location_catalog(db: Session = Depends(get_db)):
    """
    Devuelve los países y sus provincias que tienen al menos un producto
    activo y disponible. Ideal para selects dinámicos en el frontend.
    """
    rows = (
        db.query(Location.country, Location.province)
        .join(Product, Product.location_id == Location.id)
        .filter(
            Product.status == ProductStatus.active,
            Product.stock_status == StockStatus.available,
            Location.country.isnot(None),
            Location.province.isnot(None),
            Location.province != "",
        )
        .distinct()
        .order_by(Location.country, Location.province)
        .all()
    )

    grouped: dict[str, set[str]] = defaultdict(set)
    for country, province in rows:
        grouped[country].add(province)

    countries = [
        CountryEntry(country=c, provinces=sorted(grouped[c]))
        for c in sorted(grouped)
    ]
    return LocationCatalogResponse(countries=countries)


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    return _get_location_or_404(location_id, db)


@router.patch("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)
):
    location = _get_location_or_404(location_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = _get_location_or_404(location_id, db)
    db.delete(location)
    db.commit()
