from http import HTTPStatus
from uuid import uuid4


def test_product_detail_smoke(client, db):
    # создаём админа
    email = f"u_{uuid4().hex[:8]}@example.com"
    password = "x123456"

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == HTTPStatus.CREATED

    # повышаем до суперпользователя через БД
    from app.db import SessionLocal
    from app.models.user import User

    s = SessionLocal()
    u = s.query(User).filter_by(email=email).first()
    u.is_superuser = True
    s.commit()
    s.close()

    # логин
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == HTTPStatus.OK
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    suf = uuid4().hex[:6]

    # создаём бренд/category
    b = client.post("/admin/brands", json={"name": f"B{suf}", "slug": f"b{suf}"}, headers=h)
    c = client.post("/admin/categories", json={"name": f"C{suf}", "slug": f"c{suf}"}, headers=h)
    assert b.status_code == 201 and c.status_code == 201
    brand_id, cat_id = b.json()["id"], c.json()["id"]

    # создаём товар
    p = client.post(
        "/admin/products",
        json={
            "sku": f"SKU-{suf}",
            "name": f"Test phone {suf}",
            "slug": f"test-phone-{suf}",
            "brand_id": brand_id,
            "category_id": cat_id,
            "price_cents": 12345,
            "is_active": True,
        },
        headers=h,
    )
    assert p.status_code == 201
    prod_id = p.json()["id"]

    # media + inventory
    img = client.post(
        f"/admin/products/{prod_id}/images",
        json={"url": "https://picsum.photos/seed/1/600/400", "is_primary": True, "position": 0},
        headers=h,
    )
    assert img.status_code == 201, img.text

    inv = client.patch(
        f"/admin/products/{prod_id}/inventory",
        params={"qty": 2, "track_inventory": True},
        headers=h,
    )
    assert inv.status_code == 200, inv.text

    # публичная карточка
    r = client.get(f"/products/{prod_id}")
    assert r.status_code == HTTPStatus.OK
    body = r.json()
    assert body["id"] == prod_id
    assert isinstance(body["images"], list) and len(body["images"]) >= 1
    assert body["inventory_qty"] == 2
    assert body["in_stock"] is True
