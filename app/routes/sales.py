from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale import Sale
from app.models.store import Store
from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.sale import SaleListResponse, SaleResponse

router = APIRouter()


# ── Helper ─────────────────────────────────────────────────────────────────────

def _get_sale_or_404(sale_id: int, db: Session) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada",
        )
    return sale


def _user_can_view_store_sales(user: User, store: Store) -> bool:
    """Verifica si el usuario tiene permiso para ver ventas de una tienda."""
    if user.role in (UserRole.operator, UserRole.admin):
        return True
    if user.role == UserRole.seller and store.seller_id == user.id:
        return True
    return False


# ── Listar todas las ventas (solo admin) ───────────────────────────────────────

@router.get("/", response_model=SaleListResponse)
def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver todas las ventas",
        )
    total = db.query(Sale).count()
    sales = (
        db.query(Sale)
        .order_by(Sale.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "sales": sales}


# ── Ventas por tienda (seller propietario, operator, admin) ────────────────────

@router.get("/store/{store_id}", response_model=SaleListResponse)
def sales_by_store(
    store_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )
    if not _user_can_view_store_sales(current_user, store):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver las ventas de esta tienda",
        )
    query = db.query(Sale).filter(Sale.store_id == store_id)
    total = query.count()
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "sales": sales}


# ── Obtener venta por ID ───────────────────────────────────────────────────────

@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = _get_sale_or_404(sale_id, db)
    store = db.query(Store).filter(Store.id == sale.store_id).first()
    if store and not _user_can_view_store_sales(current_user, store):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta venta",
        )
    return sale
