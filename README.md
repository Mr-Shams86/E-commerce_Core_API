# 🛍️ E-commerce Core API (FastAPI)

* [![CI](https://github.com/Mr-Shams86/E-commerce_Core_API/actions/workflows/ci.yml/badge.svg)](https://github.com/Mr-Shams86/E-commerce_Core_API/actions/workflows/ci.yml)


* A minimal yet production-ready e-commerce API core: JWT-based authentication, product catalog (categories, brands, items), image handling, inventory management, public listings with filtering and sorting, and Redis-powered caching.
* Fully containerized with Docker.

## ⚙️ Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy** + **Alembic** (PostgreSQL)
- **Redis** — Caching of public listings
- **PyJWT (python-jose)** + **passlib** — JWT + bcrypt
- **Docker / docker-compose**
- **Ruff**, **pre-commit**, **GitHub Actions** — Auto linting & CI

## 📂 Project Structure

```bash
.
├── alembic/                          # ⚙️ DB migrations (Alembic)
│   ├── env.py                         # Main Alembic configuration
│   ├── script.py.mako                 # Template for migration generation
│   └── versions/                      # Migration revisions directory
│       └── 98848a648c3a_initial_schema_users_catalog_product_.py
├── alembic.ini                        # Alembic settings
│
├── app/                               # 💡 Main FastAPI application
│   ├── api/                           # 🌐 Routes and dependencies
│   │   ├── deps.py                    # Common dependencies (DB, JWT, etc.)
│   │   └── routers/                   # Endpoints separation
│   │       ├── admin_catalog.py       # Admin CRUD: brands, categories, products
│   │       ├── auth.py                # Registration / login / JWT
│   │       ├── health.py              # Server health check
│   │       ├── products.py            # Public catalog + Redis cache
│   │       └── users.py               # Users (profiles, etc.)
│   │
│   ├── core/                          # ⚙️ Core application logic
│   │   ├── cache.py                   # Redis cache configuration
│   │   ├── config.py                  # Environment settings and variables
│   │   └── security.py                # JWT, password hashing
│   │
│   ├── db.py                          # Database connection (SQLAlchemy)
│   ├── main.py                        # FastAPI entry point (uvicorn app.main:app)
│   │
│   ├── models/                        # 🧱 SQLAlchemy models
│   │   ├── catalog.py                 # Categories, brands, products, images, stock
│   │   └── user.py                    # User model
│   │
│   └── schemas/                       # 🧩 Pydantic schemas (DTOs)
│       ├── catalog.py                 # ProductRead, ProductDetail, CategoryRead, etc.
│       └── user.py                    # UserCreate, UserRead, Token, etc.
│
├── docker/                            # 🐳 Docker configurations
│   └── api.Dockerfile                 # Dockerfile for API service
│
├── docker-compose.yml                 # docker-compose for API, Postgres, Redis
├── docker-compose.override.yml        # Dev settings (hot reload, volumes)
│
├── Makefile                           # 🚀 Utilities and shortcuts
├── pyproject.toml                     # Ruff, dependencies, formatting settings
├── requirements.txt                   # Main dependencies
├── dev-requirements.txt               # Dev dependencies (pytest, pre-commit)
│
├── scripts/                           # 🧪 Helper scripts
│   └── seed_demo_data.py              # Seed demo data
│
├── tests/                             # ✅ Tests (pytest)
│   ├── api/
│   │   ├── test_auth.py               # Registration/login tests
│   │   ├── test_products.py           # Product listing tests
│   │   ├── test_products_detail.py    # Product detail tests
│   │   └── test_admin_media_inventory.py  # Images and stock tests
│   └── conftest.py                    # Common pytest fixtures
│
├── comands.txt                        # 🧠 Hints and useful commands
├── structure.txt                      # Current project structure file
├── pytest.ini                         # Pytest configuration
├── README.md                          # Project documentation
└── requirements.lock                  # (Optional) pinned dependency versions

```

## 🚀 Quick start

```bash
# 1) .env (see below) — create from the example if needed
cp .env.example .env

# 2) Run
docker compose up --build

# 3) (optional) demo data
docker compose exec api python scripts/seed_demo_data.py
```

## Access:

* 🌐 API: http://localhost:8000
* 📘 Swagger: http://localhost:8000/docs
* ❤️ Health: http://localhost:8000/healthz

## Environment variables

`.env` (базовый набор):

# FastAPI
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000

# PostgreSQL
POSTGRES_DB=ecom
POSTGRES_USER=ecom
POSTGRES_PASSWORD=ecom
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://ecom:ecom@db:5432/ecom

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
SECRET_KEY=change_me_long_random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# UID / GID (for correct container permissions)
UID=1000
GID=1000

> `Set UID/GID to match your user (id -u / id -g)`.
> `The api service in docker-compose.yml runs with user: "${UID}:${GID}"`.

## 🧱 Migrations (Alembic)

```bash
# create a migration from current models
docker compose exec api alembic revision -m "my change" --autogenerate

# apply all migrations
docker compose exec api alembic upgrade head

# history / current revision
docker compose exec api alembic history
docker compose exec api alembic current

```

## Clean DB start

```bash
docker compose down
docker volume rm e-commerce_core_api_pgdata
docker compose up --build
```

## 🔐 Authentication (JWT)

1. **Register**: `POST /auth/register` — creates a user (`is_superuser=false`).
2. **Login**: `POST /auth/login` (`application/x-www-form-urlencoded`) → `{"access_token": "...", "token_type": "bearer"}`.
3. In Swagger click **Authorize** and paste `Bearer <access_token>`.
4. **Check**: `GET /users/me`.

## 🧑‍💼 Superuser

* Admin catalog endpoints require is_superuser=true.
* In dev you can mark a user manually:

```bash
docker compose exec -T db sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "UPDATE users SET is_superuser = true WHERE email = '\''you@example.com'\'';"'
```

## Catalog (admin, superuser only)

* **Categories**

  * `POST /admin/categories` — create
  * `PATCH /admin/categories/{cat_id}` — partial update
  * `DELETE /admin/categories/{cat_id}` — delete

* **Brands**

  * `POST /admin/brands`
  * `PATCH /admin/brands/{brand_id}`
  * `DELETE /admin/brands/{brand_id}`

* **Products**

  * `POST /admin/products`
  * `PATCH /admin/products/{prod_id}`
  * `DELETE /admin/products/{prod_id}`

* **Product images**

  * `POST /admin/products/{prod_id}/images` — add image URL (supports is_primary, position)

* **Inventory**

  * `PATCH /admin/products/{prod_id}/inventory?qty=5&track_inventory=true` — inventory upsert

## ⚠️ sku and slug are unique.
* brand_id and category_id must reference existing records.

**PATCH hints**
* Only send fields that should be changed.
`brand_id`/`category_id` — must reference existing records.
`sku` and `slug` — must be unique.

## 🛒 Public product listing

`GET /products` — filters:

* q — search by name / slug
* category_id — filter by category
* brand_id — filter by brand
* sort: price_asc, price_desc, created_desc (default), created_asc
* limit — pagination (default 20, max 100), offset (default 0)

**Response** (pagination):

```json
{
  "total": 123,
  "limit": 20,
  "offset": 0,
  "items": [ { ...ProductRead }, ... ]
}
```
`GET /products/{prod_id}` — product details

**Response**
* {
  "id": 1,
  "sku": "SKU-1",
  "name": "Phone 1",
  "slug": "phone-1",
  "brand_id": 1,
  "category_id": 1,
  "price_cents": 100000,
  "is_active": true,
  "created_at": "2025-10-15T10:34:28.128Z",
  "images": [
    {"id": 10, "url": "https://picsum.photos/seed/1/600/400", "is_primary": true, "position": 0}
  ],
  "inventory_qty": 5,
  "in_stock": true
}


## 🔁 Caching (Redis)
* /products listing is cached for 120 seconds (the key includes filters/sort/pagination)

* Any admin operation on categories/brands/products/images/inventory invalidates products:* keys**инвалидирует** ключи `products:*`.

## 🧪 Request examples

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"x123456"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=demo@example.com&password=x123456' | jq -r .access_token)

# Create a brand
curl -X POST http://localhost:8000/admin/brands \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"XBrand","slug":"xbrand"}'


## Useful commands

```bash
# API logs
docker compose logs -f api

# Shell inside API container
docker compose exec api bash

# Tables in Postgres
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'

```
## 🧠 Development & tests

* Hot-reload is enabled (volumes for app/ and alembic/ are mounted).
* Pre-commit: Ruff formats/lints on commit.

## Tests & CI

* Locally:

```bash
docker compose exec -T api pytest -q
```

* CI (GitHub Actions, .github/workflows/ci.yml):

* `ruff check .`
* `ruff format --check .`
* `pytest .`

## 🚑 Troubleshooting

* **403 Forbidden on /admin/**: current user is not is_superuser=true
* **409 Conflict on product create/update**: sku or slug conflict
* **500 Internal Server Error on PATCH/POST**:

* non-existing brand_id / category_id

* unique constraint violation

* Swagger /docs is not opening:

* check docker compose ps (api must listen on 0.0.0.0:8000)

* make sure port 8000 is free

## 🧑‍💻 Author: ๛Samer Shams๖
## 📦 Repository: https://github.com/Mr-Shams86/E-commerce_Core_API
