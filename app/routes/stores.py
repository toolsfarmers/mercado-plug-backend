from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.location import Location
from app.models.store import Store
from app.models.user import User, UserRole
from app.routes.auth import get_current_user
from app.schemas.store import StoreCreate, StoreListResponse, StoreResponse, StoreUpdate

router = APIRouter()


def _get_store_or_404(store_id: int, db: Session) -> Store:
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )
    return store


@router.post("/", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden registrar tiendas",
        )

    user = db.query(User).filter(User.id == payload.seller_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario proporcionado no existe",
        )

    slug = payload.resolve_slug()

    existing_slug = db.query(Store).filter(Store.slug == slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El slug '{slug}' ya está en uso. Elige otro nombre o proporciona un slug personalizado.",
        )

    location = Location()
    db.add(location)
    db.flush()

    store = Store(
        seller_id=payload.seller_id,
        store_name=payload.store_name,
        slug=slug,
        description=payload.description,
        logo_url=payload.logo_url,
        cover_image_url=payload.cover_image_url,
        whatsapp_number=payload.whatsapp_number,
        location_id=location.id,
    )
    db.add(store)

    # El usuario pasa automáticamente a rol 'seller' al recibir una tienda
    if user.role == UserRole.buyer:
        user.role = UserRole.seller

    db.commit()
    db.refresh(store)
    return store


@router.get("/", response_model=StoreListResponse)
def list_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    seller_id: int | None = Query(None, description="Filtrar por vendedor"),
    db: Session = Depends(get_db),
):
    query = db.query(Store)
    if seller_id is not None:
        query = query.filter(Store.seller_id == seller_id)
    total = query.count()
    stores = query.offset(skip).limit(limit).all()
    return {"total": total, "stores": stores}


@router.get("/slug/{slug}", response_model=StoreResponse)
def get_store_by_slug(slug: str, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.slug == slug).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tienda no encontrada",
        )
    return store


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(store_id: int, db: Session = Depends(get_db)):
    return _get_store_or_404(store_id, db)


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(store_id: int, payload: StoreUpdate, db: Session = Depends(get_db)):
    store = _get_store_or_404(store_id, db)

    update_data = payload.model_dump(exclude_unset=True)

    if "slug" in update_data:
        conflict = (
            db.query(Store)
            .filter(Store.slug == update_data["slug"], Store.id != store_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El slug '{update_data['slug']}' ya está en uso",
            )

    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = _get_store_or_404(store_id, db)
    db.delete(store)
    db.commit()
