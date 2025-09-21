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
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    sort: Sort = Query("created_desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    # Базовые фильтры (используем один и тот же набор для items и total)
    filters = [Product.is_active.is_(True)]

    if q:
        like = f"%{q.lower()}%"
        filters.append(func.lower(Product.name).like(like))
    if category_id:
        filters.append(Product.category_id == category_id)
    if brand_id:
        filters.append(Product.brand_id == brand_id)

    # Карта сортировок
    order_map = {
        "price_asc": Product.price_cents.asc(),
        "price_desc": Product.price_cents.desc(),
        "created_desc": Product.created_at.desc(),
        "created_asc": Product.created_at.asc(),
    }

    # Запрос на элементы
    stmt_items = (
        select(Product).where(*filters).order_by(order_map[sort]).limit(limit).offset(offset)
    )
    items = db.execute(stmt_items).scalars().all()

    # Отдельный subquery по тем же фильтрам для total — без варнинга
    base_stmt = select(Product.id).where(*filters).subquery()
    total = db.scalar(select(func.count()).select_from(base_stmt))

    return Page(total=total or 0, limit=limit, offset=offset, items=items)
