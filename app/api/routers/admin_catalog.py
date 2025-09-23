from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_superuser
from app.models.catalog import Brand, Category, Product
from app.schemas.catalog import (
    BrandCreate,
    BrandRead,
    BrandUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

# Один раз требуем суперправа на весь /admin
router = APIRouter(
    prefix="/admin", tags=["admin:catalog"], dependencies=[Depends(require_superuser)]
)


# ------- Category -------
@router.post("/categories", response_model=CategoryRead)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    obj = Category(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/categories/{cat_id}", response_model=CategoryRead)
def update_category(
    cat_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
) -> CategoryRead:
    obj = db.get(Category, cat_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Category, cat_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()


# ------- Brand -------
@router.post("/brands", response_model=BrandRead)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)) -> BrandRead:
    obj = Brand(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/brands/{brand_id}", response_model=BrandRead)
def update_brand(brand_id: int, payload: BrandUpdate, db: Session = Depends(get_db)) -> BrandRead:
    obj = db.get(Brand, brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/brands/{brand_id}", status_code=204)
def delete_brand(brand_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Brand, brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()


# ------- Product -------
@router.post("/products", response_model=ProductRead)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductRead:
    obj = Product(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/products/{prod_id}", response_model=ProductRead)
def update_product(
    prod_id: int, payload: ProductUpdate, db: Session = Depends(get_db)
) -> ProductRead:
    obj = db.get(Product, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/products/{prod_id}", status_code=204)
def delete_product(prod_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Product, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
