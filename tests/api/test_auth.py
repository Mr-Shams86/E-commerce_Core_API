from http import HTTPStatus
from uuid import uuid4


def _unique_email() -> str:
    return f"u_{uuid4().hex[:8]}@example.com"


def test_register_and_login(client, db):
    email = _unique_email()
    password = "secret123"

    # регистрация
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == HTTPStatus.CREATED, r.text
    data = r.json()
    assert data["email"] == email
    assert "id" in data

    # логин через OAuth2PasswordRequestForm (form-data)
    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == HTTPStatus.OK, r.text
    token = r.json()["access_token"]

    # запрос к защищённому эндпоинту
    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == HTTPStatus.OK
    me = r.json()
    assert me["email"] == email


def test_register_conflict(client):
    email = _unique_email()
    # первая регистрация — ок
    r1 = client.post("/auth/register", json={"email": email, "password": "x123456"})
    assert r1.status_code == HTTPStatus.CREATED, r1.text
    # повторная попытка — 409 Conflict
    r2 = client.post("/auth/register", json={"email": email, "password": "x123456"})
    assert r2.status_code == HTTPStatus.CONFLICT
