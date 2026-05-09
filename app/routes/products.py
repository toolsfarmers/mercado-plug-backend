from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product, ProductStatus, ProductType, StockStatus
from app.models.store import Store
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()


def _get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == payload.store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La tienda proporcionada no existe",
        )
    if store.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden agregar productos a tiendas activas",
        )

    product = Product(
        store_id=payload.store_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
        category=payload.category,
        type=payload.type,
        images=payload.images,
        stock_status=payload.stock_status,
        whatsapp_number=store.whatsapp_number,
        location_id=store.location_id,
        delivery=payload.delivery,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    store_id: int | None = Query(None, description="Filtrar por tienda"),
    category: str | None = Query(None, description="Filtrar por categoría"),
    type: ProductType | None = Query(None, description="Filtrar por tipo: product / service"),
    stock_status: StockStatus | None = Query(None, description="Filtrar por disponibilidad"),
    delivery: bool | None = Query(None, description="Filtrar por entrega a domicilio"),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.status == ProductStatus.active)

    if store_id is not None:
        query = query.filter(Product.store_id == store_id)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if type is not None:
        query = query.filter(Product.type == type)
    if stock_status is not None:
        query = query.filter(Product.stock_status == stock_status)
    if delivery is not None:
        query = query.filter(Product.delivery == delivery)

    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "products": products}


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return _get_product_or_404(product_id, db)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
):
    product = _get_product_or_404(product_id, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = _get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()
