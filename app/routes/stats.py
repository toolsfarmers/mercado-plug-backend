from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commission import Commission, CommissionStatus
from app.models.order import Order, OrderStatus
from app.models.product import Product, ProductStatus
from app.models.sale import Sale
from app.models.store import Store
from app.models.user import User, UserRole, UserStatus
from app.routes.auth import get_current_user

router = APIRouter()


# ── Stats globales para admin ──────────────────────────────────────────────────

@router.get("/admin")
def admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver estas estadísticas",
        )

    # ── Ventas ─────────────────────────────────────────────────────────────────
    total_revenue = db.query(func.coalesce(func.sum(Sale.amount), 0)).scalar()
    total_sales = db.query(func.count(Sale.id)).scalar()

    # ── Pedidos ────────────────────────────────────────────────────────────────
    orders_by_status = {
        s.value: db.query(func.count(Order.id)).filter(Order.status == s).scalar()
        for s in OrderStatus
    }
    total_orders = db.query(func.count(Order.id)).scalar()

    # ── Comisiones ─────────────────────────────────────────────────────────────
    total_commissions_pending = db.query(
        func.coalesce(func.sum(Commission.amount), 0)
    ).filter(Commission.status == CommissionStatus.pending).scalar()
    total_commissions_collected = db.query(
        func.coalesce(func.sum(Commission.amount), 0)
    ).filter(Commission.status == CommissionStatus.paid).scalar()

    # ── Tiendas ────────────────────────────────────────────────────────────────
    total_stores = db.query(func.count(Store.id)).scalar()
    active_stores = db.query(func.count(Store.id)).filter(
        Store.status == "active"
    ).scalar()

    # ── Usuarios ───────────────────────────────────────────────────────────────
    total_users = db.query(func.count(User.id)).scalar()
    users_by_role = {
        r.value: db.query(func.count(User.id)).filter(User.role == r).scalar()
        for r in UserRole
    }
    active_users = db.query(func.count(User.id)).filter(
        User.status == UserStatus.active
    ).scalar()

    # ── Productos ──────────────────────────────────────────────────────────────
    total_products = db.query(func.count(Product.id)).filter(
        Product.status == ProductStatus.active
    ).scalar()

    # ── Top 5 tiendas por ingresos ─────────────────────────────────────────────
    top_stores_rows = (
        db.query(
            Sale.store_id,
            func.sum(Sale.amount).label("revenue"),
            func.count(Sale.id).label("sales_count"),
        )
        .group_by(Sale.store_id)
        .order_by(func.sum(Sale.amount).desc())
        .limit(5)
        .all()
    )
    store_ids = [r.store_id for r in top_stores_rows if r.store_id]
    stores_map = {s.id: s.store_name for s in db.query(Store).filter(Store.id.in_(store_ids)).all()}
    top_stores = [
        {
            "store_id": r.store_id,
            "store_name": stores_map.get(r.store_id, f"Tienda #{r.store_id}"),
            "revenue": str(r.revenue),
            "sales_count": r.sales_count,
        }
        for r in top_stores_rows
    ]

    return {
        "revenue": {
            "total": str(total_revenue),
            "total_sales": total_sales,
        },
        "commissions": {
            "pending": str(total_commissions_pending),
            "collected": str(total_commissions_collected),
        },
        "orders": {
            "total": total_orders,
            "by_status": orders_by_status,
        },
        "stores": {
            "total": total_stores,
            "active": active_stores,
        },
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": users_by_role,
        },
        "products": {
            "total_active": total_products,
        },
        "top_stores_by_revenue": top_stores,
    }


# ── Stats de tienda para vendedor ─────────────────────────────────────────────

@router.get("/store/{store_id}")
def store_stats(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )

    is_owner = store.seller_id == current_user.id
    is_privileged = current_user.role in (UserRole.operator, UserRole.admin)
    if not is_owner and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas estadísticas",
        )

    # ── Ventas ─────────────────────────────────────────────────────────────────
    total_revenue = db.query(
        func.coalesce(func.sum(Sale.amount), 0)
    ).filter(Sale.store_id == store_id).scalar()
    total_sales = db.query(func.count(Sale.id)).filter(Sale.store_id == store_id).scalar()

    # ── Pedidos ────────────────────────────────────────────────────────────────
    orders_by_status = {
        s.value: db.query(func.count(Order.id)).filter(
            Order.store_id == store_id, Order.status == s
        ).scalar()
        for s in OrderStatus
    }
    total_orders = db.query(func.count(Order.id)).filter(Order.store_id == store_id).scalar()

    # ── Comisiones ─────────────────────────────────────────────────────────────
    commission_pending = db.query(
        func.coalesce(func.sum(Commission.amount), 0)
    ).filter(
        Commission.store_id == store_id,
        Commission.status == CommissionStatus.pending,
    ).scalar()
    commission_paid = db.query(
        func.coalesce(func.sum(Commission.amount), 0)
    ).filter(
        Commission.store_id == store_id,
        Commission.status == CommissionStatus.paid,
    ).scalar()

    # ── Productos ──────────────────────────────────────────────────────────────
    total_products = db.query(func.count(Product.id)).filter(
        Product.store_id == store_id,
        Product.status == ProductStatus.active,
    ).scalar()

    # ── Top 5 productos más vendidos ───────────────────────────────────────────
    top_products_rows = (
        db.query(
            Sale.product_id,
            func.count(Sale.id).label("units_sold"),
            func.sum(Sale.amount).label("revenue"),
        )
        .filter(Sale.store_id == store_id)
        .group_by(Sale.product_id)
        .order_by(func.count(Sale.id).desc())
        .limit(5)
        .all()
    )
    product_ids = [r.product_id for r in top_products_rows if r.product_id]
    products_map = {
        p.id: p.name
        for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }
    top_products = [
        {
            "product_id": r.product_id,
            "product_name": products_map.get(r.product_id, f"Producto #{r.product_id}"),
            "units_sold": r.units_sold,
            "revenue": str(r.revenue),
        }
        for r in top_products_rows
    ]

    return {
        "store_id": store_id,
        "store_name": store.store_name,
        "commission_rate": str(store.commission_rate),
        "revenue": {
            "total": str(total_revenue),
            "total_sales": total_sales,
        },
        "orders": {
            "total": total_orders,
            "by_status": orders_by_status,
        },
        "commissions": {
            "pending": str(commission_pending),
            "paid": str(commission_paid),
        },
        "products": {
            "total_active": total_products,
        },
        "top_products_by_sales": top_products,
    }
