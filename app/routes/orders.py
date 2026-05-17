from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.sale import Sale
from app.models.store import Store
from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse, OrderStatusUpdate

router = APIRouter()


# ── Helpers de autorización ────────────────────────────────────────────────────

def _require_operator_or_admin(user: User) -> None:
    if user.role not in (UserRole.operator, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a operadores y administradores",
        )


def _get_order_or_404(order_id: int, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado",
        )
    return order


def _create_sale_for_order(order: Order, db: Session) -> None:
    """Crea automáticamente una venta cuando un pedido llega a 'delivered'."""
    existing = db.query(Sale).filter(Sale.order_id == order.id).first()
    if existing:
        return

    store = db.query(Store).filter(Store.id == order.store_id).first()
    seller_id = store.seller_id if store else None

    sale = Sale(
        order_id=order.id,
        store_id=order.store_id,
        product_id=order.product_id,
        seller_id=seller_id,
        amount=order.unit_price * order.quantity,
        currency=order.currency,
    )
    db.add(sale)


# ── Crear pedido ───────────────────────────────────────────────────────────────

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.buyer, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los compradores pueden crear pedidos",
        )

    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    order = Order(
        user_id=current_user.id,
        product_id=product.id,
        store_id=product.store_id,
        quantity=payload.quantity,
        unit_price=product.price,
        currency=product.currency,
        delivery_address=payload.delivery_address,
        notes=payload.notes,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


# ── Listar todos los pedidos (operator / admin) ────────────────────────────────

@router.get("/", response_model=OrderListResponse)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    order_status: OrderStatus | None = Query(None, alias="status"),
    store_id: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_operator_or_admin(current_user)
    query = db.query(Order)
    if order_status:
        query = query.filter(Order.status == order_status)
    if store_id:
        query = query.filter(Order.store_id == store_id)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "orders": orders}


# ── Mis pedidos (cualquier usuario autenticado) ────────────────────────────────

@router.get("/my", response_model=OrderListResponse)
def my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    order_status: OrderStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Order).filter(Order.user_id == current_user.id)
    if order_status:
        query = query.filter(Order.status == order_status)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "orders": orders}


# ── Obtener pedido por ID ──────────────────────────────────────────────────────

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = _get_order_or_404(order_id, db)
    is_owner = order.user_id == current_user.id
    is_privileged = current_user.role in (UserRole.operator, UserRole.admin)
    if not is_owner and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pedido",
        )
    return order


# ── Actualizar estado ──────────────────────────────────────────────────────────

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = _get_order_or_404(order_id, db)
    is_privileged = current_user.role in (UserRole.operator, UserRole.admin)
    is_owner = order.user_id == current_user.id

    if not is_privileged:
        # Un comprador solo puede cancelar su propio pedido si está pendiente
        if not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para modificar este pedido",
            )
        if payload.status != OrderStatus.cancelled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes cancelar tu pedido",
            )
        if order.status != OrderStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se puede cancelar un pedido en estado 'pending'",
            )

    if order.status == OrderStatus.delivered and payload.status != OrderStatus.delivered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un pedido ya entregado no puede cambiar de estado",
        )
    if order.status == OrderStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un pedido cancelado no puede cambiar de estado",
        )

    order.status = payload.status

    if payload.status == OrderStatus.delivered:
        _create_sale_for_order(order, db)

    db.commit()
    db.refresh(order)
    return order


# ── Eliminar pedido (solo admin) ───────────────────────────────────────────────

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar pedidos",
        )
    order = _get_order_or_404(order_id, db)
    db.delete(order)
    db.commit()
