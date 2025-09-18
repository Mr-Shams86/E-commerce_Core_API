from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.catalog import Product
from app.schemas.catalog import Page

router = APIRouter(prefix="/products", tags=["products"])

Sort = Literal["price_asc", "price_desc", "created_desc", "created_asc"]


@router.get("", response_model=Page)
def list_products(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    sort: Sort = Query("created_desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    stmt = select(Product).where(Product.is_active.is_(True))

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(func.lower(Product.name).like(like))
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if brand_id:
        stmt = stmt.where(Product.brand_id == brand_id)

    order_map = {
        "price_asc": Product.price_cents.asc(),
        "price_desc": Product.price_cents.desc(),
        "created_desc": Product.created_at.desc(),
        "created_asc": Product.created_at.asc(),
    }
    stmt = stmt.order_by(order_map[sort]).limit(limit).offset(offset)

    items = db.execute(stmt).scalars().all()

    total = db.scalar(
        select(func.count()).select_from(
            select(Product.id)
            .where(Product.is_active.is_(True))
            .where(Product.category_id == category_id)
            if category_id
            else select(Product.id)
        )
    )

    return Page(total=total or 0, limit=limit, offset=offset, items=items)
