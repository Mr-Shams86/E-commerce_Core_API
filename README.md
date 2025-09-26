# E-commerce Core API (FastAPI)

![CI](https://github.com/Mr-Shams86/E-commerce_Core_API/actions/workflows/ci.yml/badge.svg)

Минимальное ядро e-commerce API: аутентификация (JWT), каталог (категории, бренды, товары), картинки товаров, остатки на складе, публичный листинг с фильтрами/сортировкой и простым кешированием. Запуск — в Docker.

## Stack

* **FastAPI** + **Uvicorn**
* **SQLAlchemy** + **Alembic** (PostgreSQL)
* **Redis** (кеш листинга)
* **PyJWT (python-jose)** + **passlib** (bcrypt)
* Docker / docker-compose
* Ruff + pre-commit, GitHub Actions (lint)

## 📂 Структура

```
.
├── alembic/                  # миграции БД
│   ├── env.py
│   └── versions/
│       └── 98848a648c3a_initial_schema_users_catalog_product_.py
│
├── app/
│   ├── api/
│   │   ├── deps.py           # auth deps (get_current_user, require_superuser)
│   │   └── routers/
│   │       ├── admin_catalog.py  # admin CRUD + images/inventory
│   │       ├── auth.py           # /auth/register, /auth/login
│   │       ├── health.py         # /healthz
│   │       ├── products.py       # публичный листинг + Redis-кеш
│   │       └── users.py          # /users/me
│   ├── core/
│   │   ├── cache.py          # redis client
│   │   ├── config.py         # Settings (.env)
│   │   └── security.py       # hash/verify, JWT
│   ├── models/
│   │   ├── catalog.py        # Brand, Category, Product, ProductImage, Inventory
│   │   └── user.py
│   └── schemas/
│       ├── catalog.py        # Pydantic DTO + examples
│       └── user.py
│
├── scripts/
│   └── seed_demo_data.py     # сид демо-данных
├── tests/                    # базовые API-тесты (auth, products)
├── docker/                   # Dockerfile для api
├── docker-compose.yml        # api+db+redis
├── Makefile                  # make up, make test, make lint...
├── pyproject.toml            # ruff, deps для dev
└── README.md
```

## Быстрый старт

```bash
# 1) .env (см. ниже) — создайте при необходимости из примера
cp .env.example .env

# 2) Запуск
docker compose up --build

# 3) (опционально) демо-данные
docker compose exec api python scripts/seed_demo_data.py
```

Доступы:

* API: [http://localhost:8000](http://localhost:8000)
* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health: [http://localhost:8000/healthz](http://localhost:8000/healthz)

## Переменные окружения

`.env` (базовый набор):

```env
# FastAPI
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000

# Postgres
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

# Для корректных прав внутри контейнера
UID=1000
GID=1000
```

> `UID`/`GID` подставьте под своего пользователя (`id -u` / `id -g`).
> В `docker-compose.yml` сервис `api` запускается с `user: "${UID}:${GID}"`.

## Миграции (Alembic)

```bash
# создать миграцию из текущих моделей
docker compose exec api alembic revision -m "my change" --autogenerate

# применить все миграции
docker compose exec api alembic upgrade head

# история / текущая ревизия
docker compose exec api alembic history
docker compose exec api alembic current
```

### Чистый старт БД

```bash
docker compose down
docker volume rm e-commerce_core_api_pgdata
docker compose up --build
```

## Аутентификация (JWT)

1. **Регистрация**: `POST /auth/register` — создаёт пользователя (`is_superuser=false`).
2. **Логин**: `POST /auth/login` (`application/x-www-form-urlencoded`) → `{"access_token": "...", "token_type": "bearer"}`.
3. В Swagger нажмите **Authorize** и вставьте `Bearer <access_token>`.
4. **Проверка**: `GET /users/me`.

### Суперпользователь

Админ-эндпоинты каталога требуют `is_superuser=true`. В dev можно пометить юзера напрямую:

```bash
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "UPDATE users SET is_superuser = true WHERE email = '\''you@example.com'\'';"'
```

## Каталог (admin, только superuser)

* **Категории**

  * `POST /admin/categories` — создать
  * `PATCH /admin/categories/{cat_id}` — частичное обновление
  * `DELETE /admin/categories/{cat_id}` — удалить
* **Бренды**

  * `POST /admin/brands`
  * `PATCH /admin/brands/{brand_id}`
  * `DELETE /admin/brands/{brand_id}`
* **Товары**

  * `POST /admin/products`
  * `PATCH /admin/products/{prod_id}`
  * `DELETE /admin/products/{prod_id}`
* **Картинки товара**

  * `POST /admin/products/{prod_id}/images` — добавить URL-картинку (поддержка `is_primary`, `position`)
* **Остатки**

  * `PATCH /admin/products/{prod_id}/inventory?qty=5&track_inventory=true` — upsert остатков

**Подсказки для PATCH**
Передавайте только изменяемые поля.
`brand_id`/`category_id` — должны ссылаться на существующие записи.
`sku` и `slug` — уникальны.

## Публичный листинг товаров

`GET /products` — параметры:

* `q` — поиск по `name`/`slug`
* `category_id`, `brand_id`
* `sort`: `price_asc`, `price_desc`, `created_desc` (по умолчанию), `created_asc`
* `limit` (по умолчанию 20, максимум 100), `offset` (по умолчанию 0)

**Ответ** (пэйджинг):

```json
{
  "total": 123,
  "limit": 20,
  "offset": 0,
  "items": [ { ...ProductRead }, ... ]
}
```

### Кеширование (Redis)

Листинг `/products` кешируется на **120 секунд** (ключ включает фильтры/сортировку/пагинацию).
Любая админская операция по категориям/брендам/товарам/картинкам/остаткам **инвалидирует** ключи `products:*`.

## Полезные команды

```bash
# Логи API
docker compose logs -f api

# Шелл в контейнере API
docker compose exec api bash

# Таблицы в Postgres
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

## Разработка

* Hot-reload включён (тома с `app/` и `alembic/` смонтированы).
* Pre-commit: Ruff форматирует/линтит при коммите.

## Тесты и CI

Локально:

```bash
docker compose exec -T api pytest -q
```

CI (GitHub Actions, файл `.github/workflows/ci.yml`):

* `ruff check .`
* `ruff format --check .`

## Траблшутинг

* **403 Forbidden** на `/admin/**`: текущий пользователь не `is_superuser=true`.
* **409 Conflict** при создании/изменении товара: конфликт `sku` или `slug`.
* **500 Internal Server Error** при PATCH/POST:

  * несуществующие `brand_id`/`category_id`;
  * нарушение уникальных ограничений.
* **Swagger /docs не открывается**:

  * проверь `docker compose ps` (api должен слушать `0.0.0.0:8000`);
  * убедись, что порт 8000 свободен.
