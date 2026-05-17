from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product, ProductStatus
from app.models.saved_product import SavedProduct
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.product import ProductListResponse, ProductResponse

router = APIRouter()


@router.post("/{product_id}", status_code=status.HTTP_201_CREATED)
def save_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == ProductStatus.active,
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    already_saved = db.query(SavedProduct).filter(
        SavedProduct.user_id == current_user.id,
        SavedProduct.product_id == product_id,
    ).first()
    if already_saved:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El producto ya está guardado",
        )

    saved = SavedProduct(user_id=current_user.id, product_id=product_id)
    db.add(saved)
    db.commit()
    return {"message": "Producto guardado", "product_id": product_id}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved = db.query(SavedProduct).filter(
        SavedProduct.user_id == current_user.id,
        SavedProduct.product_id == product_id,
    ).first()
    if not saved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este producto no está en tus guardados",
        )
    db.delete(saved)
    db.commit()


@router.get("/", response_model=ProductListResponse)
def list_saved_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Product)
        .join(SavedProduct, SavedProduct.product_id == Product.id)
        .filter(SavedProduct.user_id == current_user.id)
        .order_by(SavedProduct.created_at.desc())
    )
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return {"total": total, "products": products}
