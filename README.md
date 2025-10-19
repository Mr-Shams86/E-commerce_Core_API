# 🛍️ E-commerce Core API (FastAPI)

* [![CI](https://github.com/Mr-Shams86/E-commerce_Core_API/actions/workflows/ci.yml/badge.svg)](https://github.com/Mr-Shams86/E-commerce_Core_API/actions/workflows/ci.yml)


* Минимальное ядро e-commerce API: аутентификация (JWT), каталог (категории, бренды, товары), изображения товаров, остатки на складе, публичный листинг с фильтрами/сортировкой и кешированием через Redis.
* Полностью изолировано в Docker.

## ⚙️ Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy** + **Alembic** (PostgreSQL)
- **Redis** — кеширование публичного листинга
- **PyJWT (python-jose)** + **passlib** — JWT + bcrypt
- **Docker / docker-compose**
- **Ruff**, **pre-commit**, **GitHub Actions** — автолинтинг и CI

## 📂 Структура проекта

```bash
.
.
├── alembic/                         # ⚙️ Миграции БД (Alembic)
│   ├── env.py                       # Основная конфигурация Alembic
│   ├── script.py.mako               # Шаблон для генерации миграций
│   └── versions/                    # Папка с ревизиями миграций
│       └── 98848a648c3a_initial_schema_users_catalog_product_.py
├── alembic.ini                      # Настройки Alembic
│
├── app/                             # 💡 Основное приложение FastAPI
│   ├── api/                         # 🌐 Маршруты и зависимости
│   │   ├── deps.py                  # Общие зависимости (DB, JWT и т.п.)
│   │   └── routers/                 # Разделение эндпоинтов
│   │       ├── admin_catalog.py     # CRUD для админки: бренды, категории, товары
│   │       ├── auth.py              # Регистрация / логин / JWT
│   │       ├── health.py            # Проверка статуса сервера
│   │       ├── products.py          # Публичный каталог + кеш Redis
│   │       └── users.py             # Пользователи (профиль и т.п.)
│   │
│   ├── core/                        # ⚙️ Ядро приложения
│   │   ├── cache.py                 # Настройка Redis-кеша
│   │   ├── config.py                # Настройки окружения и переменные
│   │   └── security.py              # JWT, хэширование паролей
│   │
│   ├── db.py                        # Подключение к БД (SQLAlchemy)
│   ├── main.py                      # Точка входа FastAPI (uvicorn app.main:app)
│   │
│   ├── models/                      # 🧱 SQLAlchemy модели
│   │   ├── catalog.py               # Категории, бренды, товары, изображения, остатки
│   │   └── user.py                  # Модель пользователя
│   │
│   └── schemas/                     # 🧩 Pydantic-схемы (DTO)
│       ├── catalog.py               # ProductRead, ProductDetail, CategoryRead и др.
│       └── user.py                  # UserCreate, UserRead, Token и т.п.
│
├── docker/                          # 🐳 Docker-конфигурации
│   └── api.Dockerfile               # Dockerfile для сервиса API
│
├── docker-compose.yml               # docker-compose для API, Postgres, Redis
├── docker-compose.override.yml      # dev-настройки (hot reload, volumes)
│
├── Makefile                         # 🚀 Утилиты и короткие команды
├── pyproject.toml                   # Настройки Ruff, зависимостей и форматирования
├── requirements.txt                 # Основные зависимости
├── dev-requirements.txt             # Dev-зависимости (pytest, pre-commit)
│
├── scripts/                         # 🧪 Вспомогательные скрипты
│   └── seed_demo_data.py            # Заполнение демо-данными
│
├── tests/                           # ✅ Тесты (pytest)
│   ├── api/
│   │   ├── test_auth.py             # Тесты регистрации/логина
│   │   ├── test_products.py         # Тест листинга товаров
│   │   ├── test_products_detail.py  # Тест карточки товара
│   │   └── test_admin_media_inventory.py  # Тест изображений и остатков
│   └── conftest.py                  # Общие фикстуры pytest
│
├── comands.txt                      # 🧠 Подсказки и полезные команды
├── structure.txt                    # Текущий файл со структурой проекта
├── pytest.ini                       # Конфигурация pytest
├── README.md                        # Документация проекта
└── requirements.lock                # (опционально) зафиксированные версии зависимостей


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

* 🌐 API: http://localhost:8000
* 📘 Swagger: http://localhost:8000/docs
* ❤️ Health: http://localhost:8000/healthz

## Переменные окружения

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

# UID / GID (для корректных прав в контейнере)
UID=1000
GID=1000

> `UID`/`GID` подставьте под своего пользователя (`id -u` / `id -g`).
> В `docker-compose.yml` сервис `api` запускается с `user: "${UID}:${GID}"`.

## 🧱 Миграции (Alembic)

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

## 🔐 Аутентификация (JWT)

1. **Регистрация**: `POST /auth/register` — создаёт пользователя (`is_superuser=false`).
2. **Логин**: `POST /auth/login` (`application/x-www-form-urlencoded`) → `{"access_token": "...", "token_type": "bearer"}`.
3. В Swagger нажмите **Authorize** и вставьте `Bearer <access_token>`.
4. **Проверка**: `GET /users/me`.

### 🧑‍💼 Суперпользователь

Админ-эндпоинты каталога требуют `is_superuser=true`. В dev можно пометить юзера напрямую:

```bash
docker compose exec -T db sh -lc \
'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "UPDATE users SET is_superuser = true WHERE email = '\''you@example.com'\'';"'
```

## 🧩 Каталог (admin, только superuser)

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

⚠️ sku и slug уникальны.
brand_id и category_id должны ссылаться на существующие записи.

**Подсказки для PATCH**
Передавайте только изменяемые поля.
`brand_id`/`category_id` — должны ссылаться на существующие записи.
`sku` и `slug` — уникальны.

## 🛒 Публичный листинг товаров

`GET /products` — фильтры:

* `q` — поиск по  поиск по имени `name`/`slug`
* `category_id`,  фильтр по категории
* `brand_id`      фильтр по бренду
* `sort`:         `price_asc`, `price_desc`, `created_desc` (по умолчанию), `created_asc`
* `limit`         пагинация (по умолчанию 20, максимум 100), `offset` (по умолчанию 0)

**Ответ** (пэйджинг):

```json
{
  "total": 123,
  "limit": 20,
  "offset": 0,
  "items": [ { ...ProductRead }, ... ]
}
```
`GET /products/{prod_id}` — карточка товара

**Ответ**
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


### Кеширование (Redis)

* Листинг `/products` кешируется на **120 секунд** (ключ включает фильтры/сортировку/пагинацию).
* Любая админская операция по категориям/брендам/товарам/картинкам/остаткам **инвалидирует** ключи `products:*`.

## 🧪 Примеры запросов
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"x123456"}'

# Логин
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=demo@example.com&password=x123456' | jq -r .access_token)

# Создать бренд
curl -X POST http://localhost:8000/admin/brands \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"XBrand","slug":"xbrand"}'


## Полезные команды

```bash
# Логи API
docker compose logs -f api

# Шелл в контейнере API
docker compose exec api bash

# Таблицы в Postgres
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

## 🧠 Разработка и тесты

* Hot-reload включён (тома с `app/` и `alembic/` смонтированы).
* Pre-commit: Ruff форматирует/линтит при коммите.

## Тесты и CI

* Локально:

```bash
docker compose exec -T api pytest -q
```

CI (GitHub Actions, файл `.github/workflows/ci.yml`):

* `ruff check .`
* `ruff format --check .`
* `pytest .`

## 🚑 Траблшутинг

* **403 Forbidden** на `/admin/**`: текущий пользователь не `is_superuser=true`.
* **409 Conflict** при создании/изменении товара: конфликт `sku` или `slug`.
* **500 Internal Server Error** при PATCH/POST:

  * несуществующие `brand_id`/`category_id`;
  * нарушение уникальных ограничений.
  * **Swagger /docs не открывается**:

  * проверь `docker compose ps` (api должен слушать `0.0.0.0:8000`);
  * убедись, что порт 8000 свободен.

## 🧭 Roadmap
- [ ] Корзина и заказы
- [ ] RBAC (admin / manager / user)
- [ ] MinIO / S3 для картинок
- [ ] Полнотекстовый поиск (pg_trgm / FTS)
- [ ] Продовый деплой (Railway / Render / VPS)

## 🧑‍💻 Автор: Samer Shamsi
## 📦Репозиторий:https://github.com/Mr-Shams86/E-commerce_Core_API
