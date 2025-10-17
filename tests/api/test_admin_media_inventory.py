from http import HTTPStatus
from uuid import uuid4


def _u() -> str:
    return f"u_{uuid4().hex[:6]}@example.com"


def _sfx() -> str:
    return uuid4().hex[:6]


def _make_admin_token(client) -> str:
    email = _u()
    password = "x123456"

    # регистрируем обычного пользователя
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == HTTPStatus.CREATED, r.text

    # повышаем до суперпользователя через БД
    from app.db import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    try:
        u = db.query(User).filter_by(email=email).first()
        u.is_superuser = True
        db.commit()
    finally:
        db.close()

    # логин (OAuth2PasswordRequestForm → form-data)
    r = client.post("/auth/login", data={"username": email, "password": password})
    assert r.status_code == HTTPStatus.OK, r.text
    return r.json()["access_token"]


def test_admin_images_and_inventory_flow(client, db):
    token = _make_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    s = _sfx()

    # создаём бренд
    b = client.post(
        "/admin/brands",
        json={"name": f"XBrand-{s}", "slug": f"xbrand-{s}"},
        headers=headers,
    )
    assert b.status_code == 201, b.text
    brand_id = b.json()["id"]

    # создаём категорию
    c = client.post(
        "/admin/categories",
        json={"name": f"Phones-{s}", "slug": f"phones-{s}"},
        headers=headers,
    )
    assert c.status_code == 201, c.text
    cat_id = c.json()["id"]

    # создаём товар
    p = client.post(
        "/admin/products",
        json={
            "sku": f"SKU-{s}",
            "name": f"Phone {s}",
            "slug": f"phone-{s}",
            "brand_id": brand_id,
            "category_id": cat_id,
            "price_cents": 100000,
            "is_active": True,
        },
        headers=headers,
    )
    assert p.status_code == 201, p.text
    prod_id = p.json()["id"]

    # добавляем картинку
    img = client.post(
        f"/admin/products/{prod_id}/images",
        json={"url": "https://picsum.photos/seed/1/600/400", "is_primary": True, "position": 0},
        headers=headers,
    )
    assert img.status_code == 201, img.text
    assert img.json()["is_primary"] is True

    # апсёрт инвентаря
    inv = client.patch(
        f"/admin/products/{prod_id}/inventory",
        params={"qty": 5, "track_inventory": True},
        headers=headers,
    )
    assert inv.status_code == 200, inv.text
    assert inv.json()["qty"] == 5


def test_admin_requires_superuser_403(client):
    # без токена доступ к /admin/* закрыт
    res = client.post("/admin/brands", json={"name": "N", "slug": "n"})
    assert res.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
