from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.interaction import InteractionAction, ProductInteraction
from app.models.product import Product
from app.models.store import Store
from app.schemas.interaction import (
    AdminStatsResponse,
    InteractionCreate,
    InteractionResponse,
    SellerStatsResponse,
    UserInterestsResponse,
)

router = APIRouter()


# ── Registrar interacción ──────────────────────────────────────────────────────

@router.post("/", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def register_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    interaction = ProductInteraction(
        product_id=payload.product_id,
        store_id=product.store_id,
        user_id=payload.user_id,
        action=payload.action,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


# ── Stats para vendedor ────────────────────────────────────────────────────────

@router.get("/stats/store/{store_id}", response_model=SellerStatsResponse)
def seller_stats(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )

    base_query = db.query(ProductInteraction).filter(
        ProductInteraction.store_id == store_id
    )
    total = base_query.count()

    # Interacciones por producto
    by_product_rows = (
        db.query(
            ProductInteraction.product_id,
            Product.name,
            func.count(ProductInteraction.id).label("count"),
        )
        .join(Product, Product.id == ProductInteraction.product_id)
        .filter(ProductInteraction.store_id == store_id)
        .group_by(ProductInteraction.product_id, Product.name)
        .order_by(func.count(ProductInteraction.id).desc())
        .all()
    )
    by_product = [
        {"product_id": r.product_id, "product_name": r.name, "count": r.count}
        for r in by_product_rows
    ]

    # Interacciones por acción
    by_action_rows = (
        db.query(
            ProductInteraction.action,
            func.count(ProductInteraction.id).label("count"),
        )
        .filter(ProductInteraction.store_id == store_id)
        .group_by(ProductInteraction.action)
        .order_by(func.count(ProductInteraction.id).desc())
        .all()
    )
    by_action = [{"action": r.action, "count": r.count} for r in by_action_rows]

    # Interacciones por día (últimos 30 días)
    by_date_rows = (
        db.query(
            func.date(ProductInteraction.date).label("day"),
            func.count(ProductInteraction.id).label("count"),
        )
        .filter(ProductInteraction.store_id == store_id)
        .group_by(func.date(ProductInteraction.date))
        .order_by(func.date(ProductInteraction.date).asc())
        .limit(30)
        .all()
    )
    by_date = [{"date": str(r.day), "count": r.count} for r in by_date_rows]

    return {
        "store_id": store_id,
        "total_interactions": total,
        "by_product": by_product,
        "by_action": by_action,
        "by_date": by_date,
    }


# ── Stats globales (admin) ─────────────────────────────────────────────────────

@router.get("/stats/admin", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db)):
    total = db.query(ProductInteraction).count()

    # Top tiendas por interacciones
    by_store_rows = (
        db.query(
            ProductInteraction.store_id,
            Store.store_name,
            func.count(ProductInteraction.id).label("count"),
        )
        .join(Store, Store.id == ProductInteraction.store_id)
        .group_by(ProductInteraction.store_id, Store.store_name)
        .order_by(func.count(ProductInteraction.id).desc())
        .limit(20)
        .all()
    )
    by_store = [
        {"store_id": r.store_id, "store_name": r.store_name, "count": r.count}
        for r in by_store_rows
    ]

    # Por acción
    by_action_rows = (
        db.query(
            ProductInteraction.action,
            func.count(ProductInteraction.id).label("count"),
        )
        .group_by(ProductInteraction.action)
        .order_by(func.count(ProductInteraction.id).desc())
        .all()
    )
    by_action = [{"action": r.action, "count": r.count} for r in by_action_rows]

    # Por día (últimos 30 días)
    by_date_rows = (
        db.query(
            func.date(ProductInteraction.date).label("day"),
            func.count(ProductInteraction.id).label("count"),
        )
        .group_by(func.date(ProductInteraction.date))
        .order_by(func.date(ProductInteraction.date).asc())
        .limit(30)
        .all()
    )
    by_date = [{"date": str(r.day), "count": r.count} for r in by_date_rows]

    return {
        "total_interactions": total,
        "by_store": by_store,
        "by_action": by_action,
        "by_date": by_date,
    }


# ── User interests ─────────────────────────────────────────────────────────────

@router.get("/users/{user_id}/interests", response_model=UserInterestsResponse)
def user_interests(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(
            Product.category,
            func.count(ProductInteraction.id).label("click_count"),
        )
        .join(Product, Product.id == ProductInteraction.product_id)
        .filter(
            ProductInteraction.user_id == user_id,
            ProductInteraction.action == InteractionAction.click_buy_product,
            Product.category.isnot(None),
        )
        .group_by(Product.category)
        .order_by(func.count(ProductInteraction.id).desc())
        .limit(10)
        .all()
    )

    top_categories = [
        {"category": r.category, "click_count": r.click_count} for r in rows
    ]

    return {"user_id": user_id, "top_categories": top_categories}
