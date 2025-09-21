from datetime import datetime

from app.db import SessionLocal
from app.models.catalog import Brand, Category, Product


def get_or_create(db, model, **kw):
    obj = db.query(model).filter_by(**kw).first()
    if obj:
        return obj, False
    obj = model(**kw)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj, True


def main():
    db = SessionLocal()

    # Brands
    apple, _ = get_or_create(db, Brand, name="Apple", slug="apple")
    samsung, _ = get_or_create(db, Brand, name="Samsung", slug="samsung")

    # Categories
    phones, _ = get_or_create(db, Category, name="Smartphones", slug="smartphones")

    # Products (только FK — без передачи relationship-полей)
    products = [
        dict(
            sku="IP14-128-BL",
            name="iPhone 14 128 Black",
            slug="iphone-14-128-black",
            brand_id=apple.id,
            category_id=phones.id,
            price_cents=700_000,
            is_active=True,
        ),
        dict(
            sku="IP14-128-MN",
            name="iPhone 14 128GB Midnight",
            slug="iphone-14-128-midnight",
            brand_id=apple.id,
            category_id=phones.id,
            price_cents=690_000,
            is_active=True,
        ),
        dict(
            sku="SM-S24",
            name="Galaxy s24",
            slug="galaxy-s24",
            brand_id=samsung.id,
            category_id=phones.id,
            price_cents=650_000,
            is_active=True,
        ),
    ]

    for p in products:
        exist = db.query(Product).filter_by(sku=p["sku"]).first()
        if not exist:
            obj = Product(**p, created_at=datetime.utcnow())
            db.add(obj)

    db.commit()
    db.close()
    print("✅ Seed completed successfully.")


if __name__ == "__main__":
    main()
