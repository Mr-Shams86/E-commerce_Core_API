def test_sort_price_desc(client, sample_catalog):
    r = client.get("/products?sort=price_desc&limit=3")
    assert r.status_code == 200
    prices = [p["price_cents"] for p in r.json()["items"]]
    assert prices == sorted(prices, reverse=True)


def test_filter_by_brand(client, sample_catalog):
    r = client.get(f"/products?brand_id={sample_catalog['brand_id']}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_filter_by_category(client, sample_catalog):
    r = client.get(f"/products?category_id={sample_catalog['category_id']}")
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_pagination(client, sample_catalog):
    r1 = client.get("/products?limit=1&offset=0")
    r2 = client.get("/products?limit=1&offset=1")
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["items"][0]["id"] != r2.json()["items"][0]["id"]


def test_products_sort_price_desc(client, db):
    r = client.get("/products?sort=price_desc&limit=5")
    assert r.status_code == 200
    data = r.json()
    prices = [p["price_cents"] for p in data["items"]]
    assert prices == sorted(prices, reverse=True)
