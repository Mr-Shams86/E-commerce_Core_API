from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models.catalog import Brand, Category, Product


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        # Откат незакоммиченных изменений и закрытие сессии
        session.rollback()
        session.close()


def get_or_create(session, model, **kwargs):
    obj = session.query(model).filter_by(**kwargs).first()
    if obj:
        return obj
    obj = model(**kwargs)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@pytest.fixture()
def sample_catalog(db):
    # Бренд/категория — «idempotent»
    brand = get_or_create(db, Brand, name="TestBrand", slug="testbrand")
    cat = get_or_create(db, Category, name="TestCat", slug="testcat")

    # На всякий случай удалим возможные продукты с теми же SKU
    # (если сид или прошлый тест их оставил)
    db.query(Product).filter(Product.sku.in_(["A1", "B1", "C1"])).delete(synchronize_session=False)
    db.commit()

    items = [
        Product(
            sku="A1",
            name="Alpha",
            slug="alpha",
            brand_id=brand.id,
            category_id=cat.id,
            price_cents=100,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        Product(
            sku="B1",
            name="Beta",
            slug="beta",
            brand_id=brand.id,
            category_id=cat.id,
            price_cents=200,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        Product(
            sku="C1",
            name="Gamma",
            slug="gamma",
            brand_id=brand.id,
            category_id=cat.id,
            price_cents=150,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
    ]
    db.add_all(items)
    db.commit()

    return {"brand_id": brand.id, "category_id": cat.id}
