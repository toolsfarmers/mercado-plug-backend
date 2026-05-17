from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commission import Commission, CommissionPayment, CommissionStatus
from app.models.store import Store
from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.commission import (
    CommissionListResponse,
    CommissionPaymentListResponse,
    CommissionPaymentResponse,
    CommissionSummaryItem,
    CommissionSummaryResponse,
    SettleRequest,
    StoreBalanceResponse,
)

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _require_operator_or_admin(user: User) -> None:
    if user.role not in (UserRole.operator, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a operadores y administradores",
        )


def _get_store_or_404(store_id: int, db: Session) -> Store:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )
    return store


def _can_view_store(user: User, store: Store) -> bool:
    if user.role in (UserRole.operator, UserRole.admin):
        return True
    if user.role == UserRole.seller and store.seller_id == user.id:
        return True
    return False


# ── Resumen global (admin) ─────────────────────────────────────────────────────

@router.get("/summary", response_model=CommissionSummaryResponse)
def commission_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden ver el resumen global",
        )

    rows = (
        db.query(
            Commission.store_id,
            func.count(Commission.id).label("pending_count"),
            func.sum(Commission.amount).label("pending_amount"),
        )
        .filter(Commission.status == CommissionStatus.pending)
        .group_by(Commission.store_id)
        .all()
    )

    store_ids = [r.store_id for r in rows if r.store_id]
    stores = {s.id: s for s in db.query(Store).filter(Store.id.in_(store_ids)).all()}

    items = []
    total_pending = Decimal("0")
    for row in rows:
        store = stores.get(row.store_id)
        store_name = store.store_name if store else f"Tienda #{row.store_id}"
        rate = store.commission_rate if store else Decimal("0")
        amount = Decimal(str(row.pending_amount or 0))
        total_pending += amount
        items.append(
            CommissionSummaryItem(
                store_id=row.store_id or 0,
                store_name=store_name,
                commission_rate=rate,
                pending_count=row.pending_count,
                pending_amount=amount,
            )
        )

    items.sort(key=lambda x: x.pending_amount, reverse=True)

    return CommissionSummaryResponse(
        total_stores_with_debt=len(items),
        total_pending_amount=total_pending,
        stores=items,
    )


# ── Balance de una tienda ──────────────────────────────────────────────────────

@router.get("/store/{store_id}/balance", response_model=StoreBalanceResponse)
def store_balance(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, db)
    if not _can_view_store(current_user, store):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta información",
        )

    result = (
        db.query(
            func.count(Commission.id).label("pending_count"),
            func.coalesce(func.sum(Commission.amount), 0).label("pending_amount"),
        )
        .filter(
            Commission.store_id == store_id,
            Commission.status == CommissionStatus.pending,
        )
        .first()
    )

    return StoreBalanceResponse(
        store_id=store.id,
        store_name=store.store_name,
        commission_rate=store.commission_rate,
        pending_count=result.pending_count,
        pending_amount=Decimal(str(result.pending_amount)),
    )


# ── Historial de comisiones de una tienda ──────────────────────────────────────

@router.get("/store/{store_id}/history", response_model=CommissionListResponse)
def store_commission_history(
    store_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    commission_status: CommissionStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_operator_or_admin(current_user)
    _get_store_or_404(store_id, db)

    query = db.query(Commission).filter(Commission.store_id == store_id)
    if commission_status:
        query = query.filter(Commission.status == commission_status)

    total = query.count()
    commissions = query.order_by(Commission.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "commissions": commissions}


# ── Historial de pagos de una tienda ───────────────────────────────────────────

@router.get("/store/{store_id}/payments", response_model=CommissionPaymentListResponse)
def store_payment_history(
    store_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, db)
    if not _can_view_store(current_user, store):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta información",
        )

    query = db.query(CommissionPayment).filter(CommissionPayment.store_id == store_id)
    total = query.count()
    payments = query.order_by(CommissionPayment.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "payments": payments}


# ── Liquidar deuda de una tienda ───────────────────────────────────────────────

@router.post("/store/{store_id}/settle", response_model=CommissionPaymentResponse, status_code=status.HTTP_201_CREATED)
def settle_store_commissions(
    store_id: int,
    payload: SettleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_operator_or_admin(current_user)
    _get_store_or_404(store_id, db)

    pending = (
        db.query(Commission)
        .filter(
            Commission.store_id == store_id,
            Commission.status == CommissionStatus.pending,
        )
        .all()
    )

    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta tienda no tiene comisiones pendientes",
        )

    total_amount = sum(c.amount for c in pending)
    for commission in pending:
        commission.status = CommissionStatus.paid

    payment = CommissionPayment(
        store_id=store_id,
        amount_paid=total_amount,
        commissions_count=len(pending),
        notes=payload.notes,
        settled_by=current_user.id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
