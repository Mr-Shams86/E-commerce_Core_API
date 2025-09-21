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
        session.rollback()
        session.close()


@pytest.fixture()
def sample_catalog(db):
    brand = Brand(name="TestBrand", slug="testbrand")
    cat = Category(name="TestCat", slug="testcat")

    db.add_all([brand, cat])
    db.commit()
    db.refresh(brand)
    db.refresh(cat)

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
