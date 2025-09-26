from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_superuser
from app.core.cache import get_redis
from app.models.catalog import Brand, Category, Inventory, Product, ProductImage
from app.schemas.catalog import (
    BrandCreate,
    BrandRead,
    BrandUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    InventoryOut,
    ProductCreate,
    ProductImageIn,
    ProductImageOut,
    ProductRead,
    ProductUpdate,
)

# Один раз требуем суперправа на весь /admin
router = APIRouter(
    prefix="/admin",
    tags=["admin:catalog"],
    dependencies=[Depends(require_superuser)],
)


def _invalidate_products_cache() -> None:
    try:
        r = get_redis()
        if r:
            for k in r.scan_iter(match="products:*"):
                r.delete(k)
    except Exception:
        pass


# ------- Category -------
@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=201,
    summary="Create Category",
    description="Создать категорию каталога.",
    responses={201: {"description": "Created"}, 403: {"description": "Forbidden"}},
)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    obj = Category(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.patch(
    "/categories/{cat_id}",
    response_model=CategoryRead,
    summary="Update Category",
    description="Частично обновить категорию каталога.",
    responses={
        200: {"description": "ok"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def update_category(cat_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)) -> CategoryRead:
    obj = db.get(Category, cat_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.delete(
    "/categories/{cat_id}",
    status_code=204,
    summary="Delete Category",
    description="Удалить категорию.",
    responses={
        204: {"description": "No Content"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def delete_category(cat_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Category, cat_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    _invalidate_products_cache()
    return None


# ------- Brand -------
@router.post(
    "/brands",
    response_model=BrandRead,
    status_code=201,
    summary="Create Brand",
    description="Создать бренд.",
    responses={201: {"description": "Created"}, 403: {"description": "Forbidden"}},
)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)) -> BrandRead:
    obj = Brand(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.patch(
    "/brands/{brand_id}",
    response_model=BrandRead,
    summary="Update Brand",
    description="частично обновить бренд.",
    responses={
        200: {"description": "ok"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def update_brand(brand_id: int, payload: BrandUpdate, db: Session = Depends(get_db)) -> BrandRead:
    obj = db.get(Brand, brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.delete(
    "/brands/{brand_id}",
    status_code=204,
    summary="Delete Brand",
    description="Удалить бренд.",
    responses={
        204: {"description": "No Content"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def delete_brand(brand_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Brand, brand_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    _invalidate_products_cache()
    return None


# ------- Product -------
@router.post(
    "/products",
    response_model=ProductRead,
    status_code=201,
    summary="Create Product",
    description="Создать товар.",
    responses={201: {"description": "Created"}, 403: {"description": "Forbidden"}},
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductRead:
    obj = Product(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.patch(
    "/products/{prod_id}",
    response_model=ProductRead,
    summary="Update Product",
    description="Частично обновить товар.",
    responses={
        200: {"description": "ok"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def update_product(prod_id: int, payload: ProductUpdate, db: Session = Depends(get_db)) -> ProductRead:
    obj = db.get(Product, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)

    db.commit()
    db.refresh(obj)
    _invalidate_products_cache()
    return obj


@router.delete(
    "/products/{prod_id}",
    status_code=204,
    summary="Delete Product",
    description="Удалить товар.",
    responses={
        204: {"description": "No Content"},
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
    },
)
def delete_product(prod_id: int, db: Session = Depends(get_db)) -> None:
    obj = db.get(Product, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(obj)
    db.commit()
    _invalidate_products_cache()
    return None


@router.post(
    "/products/{prod_id}/images",
    response_model=ProductImageOut,
    status_code=201,
    summary="Add Product Image",
    description="Добавить изображение товара. Если 'is_primary=true', все остальные для товара снимаются.",
    responses={
        201: {"description": "Created"},
        404: {"description": "Product not found"},
        403: {"description": "Forbidden"},
    },
)
def add_product_image(prod_id: int, data: ProductImageIn, db: Session = Depends(get_db)) -> ProductImageOut:
    product = db.get(Product, prod_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if data.is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == prod_id,
            ProductImage.is_primary.is_(True),
        ).update({"is_primary": False})

    img = ProductImage(
        product_id=prod_id,
        url=str(data.url),
        is_primary=data.is_primary,
        position=data.position,
    )
    db.add(img)
    db.commit()
    db.refresh(img)
    _invalidate_products_cache()
    return img


@router.patch(
    "/products/{prod_id}/inventory",
    response_model=InventoryOut,
    summary="Upsert Inventory",
    description="Создать/обновить остаток товара.",
    responses={
        200: {"description": "ok"},
        404: {"description": "Product not found"},
        403: {"description": "Forbidden"},
    },
)
def upsert_inventory(
    prod_id: int,
    qty: int,
    track_inventory: bool,
    db: Session = Depends(get_db),
) -> InventoryOut:
    product = db.get(Product, prod_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inv = db.get(Inventory, prod_id)
    if not inv:
        inv = Inventory(product_id=prod_id, qty=qty, track_inventory=track_inventory)
        db.add(inv)
    else:
        inv.qty = qty
        inv.track_inventory = track_inventory

    db.commit()
    _invalidate_products_cache()
    return InventoryOut(product_id=prod_id, qty=inv.qty, track_inventory=inv.track_inventory)
