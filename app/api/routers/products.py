import json
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.cache import get_redis
from app.models.catalog import Product
from app.schemas.catalog import Page

router = APIRouter(prefix="/products", tags=["products"])

Sort = Literal["price_asc", "price_desc", "created_desc", "created_asc"]


@router.get(
    "",
    response_model=Page,
    summary="List Products",
    description="Публичный листинг товаров с фильтрами/сортировкой/пагинацией.",
    responses={
        200: {"description": "ok"},
        422: {"description": "Validation error"},
    },
)
def list_products(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Поиск по имени (ILIKE)"),
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    brand_id: Optional[int] = Query(None, description="Фильтр по бренду"),
    sort: Sort = Query("created_desc", description="Сортировка"),
    limit: int = Query(20, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
):
    r = get_redis()
    cache_key = f"products:{q or ''}:{category_id or ''}:{brand_id or ''}:{sort}:{limit}:{offset}"

    if r is not None:
        try:
            cached = r.get(cache_key)
            if cached:
                if isinstance(cached, bytes):
                    cached = cached.decode("utf-8")
                return json.loads(cached)
        except Exception:
            pass

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
    stmt_items = select(Product).where(*filters).order_by(order_map[sort]).limit(limit).offset(offset)
    items = db.execute(stmt_items).scalars().all()

    # total через subquery, чтобы не ловить SADeprecationWarning
    base_stmt = select(Product.id).where(*filters).subquery()
    total = db.scalar(select(func.count()).select_from(base_stmt)) or 0

    result = Page(total=total, limit=limit, offset=offset, items=items)

    # Redis: записываем на 120 секунд
    if r is not None:
        try:
            r.setex(cache_key, 120, json.dumps(result.model_dump(mode="json")))
        except Exception:
            pass

    return result
