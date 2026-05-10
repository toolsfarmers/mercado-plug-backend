from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import InteractionAction, ProductInteraction
from app.models.location import Location
from app.models.product import Product, ProductStatus, ProductType, StockStatus
from app.models.store import Store
from app.schemas.product import (
    FeedResponse,
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    SortBy,
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


def _apply_filters_and_sort(query, *, search, store_id, category, type,
                             stock_status, delivery, min_price, max_price,
                             province, municipality, sort_by, db):
    """Aplica todos los filtros y ordenamiento a la query."""

    if search:
        term = f"%{search}%"
        query = query.filter(
            Product.name.ilike(term) | Product.description.ilike(term)
        )
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
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if province:
        query = query.join(Location, Location.id == Product.location_id).filter(
            Location.province.ilike(f"%{province}%")
        )
    if municipality:
        if not province:
            query = query.join(Location, Location.id == Product.location_id)
        query = query.filter(Location.municipality.ilike(f"%{municipality}%"))

    # Ordenamiento
    if sort_by == SortBy.price_asc:
        query = query.order_by(Product.price.asc())
    elif sort_by == SortBy.price_desc:
        query = query.order_by(Product.price.desc())
    elif sort_by == SortBy.most_interacted:
        interaction_count = (
            db.query(
                ProductInteraction.product_id,
                func.count(ProductInteraction.id).label("icount"),
            )
            .group_by(ProductInteraction.product_id)
            .subquery()
        )
        query = (
            query.outerjoin(
                interaction_count,
                interaction_count.c.product_id == Product.id,
            )
            .order_by(func.coalesce(interaction_count.c.icount, 0).desc())
        )
    else:
        query = query.order_by(Product.created_at.desc())

    return query


# ── Crear producto ─────────────────────────────────────────────────────────────

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


# ── Listado con filtros y búsqueda ─────────────────────────────────────────────

@router.get("/", response_model=ProductListResponse)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Búsqueda en nombre y descripción"),
    store_id: int | None = Query(None, description="Filtrar por tienda"),
    category: str | None = Query(None, description="Filtrar por categoría"),
    type: ProductType | None = Query(None, description="product / service"),
    stock_status: StockStatus | None = Query(None, description="available / unavailable"),
    delivery: bool | None = Query(None, description="Filtrar por entrega a domicilio"),
    min_price: Decimal | None = Query(None, ge=0, description="Precio mínimo"),
    max_price: Decimal | None = Query(None, ge=0, description="Precio máximo"),
    province: str | None = Query(None, description="Filtrar por provincia"),
    municipality: str | None = Query(None, description="Filtrar por municipio"),
    sort_by: SortBy = Query(SortBy.newest, description="newest | price_asc | price_desc | most_interacted"),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.status == ProductStatus.active)
    query = _apply_filters_and_sort(
        query, search=search, store_id=store_id, category=category, type=type,
        stock_status=stock_status, delivery=delivery, min_price=min_price,
        max_price=max_price, province=province, municipality=municipality,
        sort_by=sort_by, db=db,
    )
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return {"total": total, "products": products}


# ── Feed personalizado ─────────────────────────────────────────────────────────

@router.get("/feed", response_model=FeedResponse)
def product_feed(
    user_id: int | None = Query(None, description="ID del usuario para feed personalizado. Omitir para trending."),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    base = db.query(Product).filter(
        Product.status == ProductStatus.active,
        Product.stock_status == StockStatus.available,
    )

    if user_id:
        # Top 5 categorías más clickeadas por este usuario
        top_cats = (
            db.query(Product.category)
            .join(ProductInteraction, ProductInteraction.product_id == Product.id)
            .filter(
                ProductInteraction.user_id == user_id,
                ProductInteraction.action == InteractionAction.click_buy_product,
                Product.category.isnot(None),
            )
            .group_by(Product.category)
            .order_by(func.count(ProductInteraction.id).desc())
            .limit(5)
            .all()
        )
        categories = [row.category for row in top_cats]

        if categories:
            query = base.filter(Product.category.in_(categories))
            interaction_count = (
                db.query(
                    ProductInteraction.product_id,
                    func.count(ProductInteraction.id).label("icount"),
                )
                .group_by(ProductInteraction.product_id)
                .subquery()
            )
            query = (
                query.outerjoin(
                    interaction_count,
                    interaction_count.c.product_id == Product.id,
                )
                .order_by(func.coalesce(interaction_count.c.icount, 0).desc())
            )
            total = query.count()
            products = query.offset(skip).limit(limit).all()
            return {"feed_type": "personalized", "total": total, "products": products}

    # Sin usuario o sin historial → trending (más interactuados)
    interaction_count = (
        db.query(
            ProductInteraction.product_id,
            func.count(ProductInteraction.id).label("icount"),
        )
        .group_by(ProductInteraction.product_id)
        .subquery()
    )
    query = (
        base.outerjoin(
            interaction_count,
            interaction_count.c.product_id == Product.id,
        )
        .order_by(func.coalesce(interaction_count.c.icount, 0).desc())
    )
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return {"feed_type": "trending", "total": total, "products": products}


# ── Obtener, actualizar, eliminar ──────────────────────────────────────────────

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
