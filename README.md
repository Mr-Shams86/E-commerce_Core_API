# E-commerce Core API (FastAPI)

Минимальное ядро API для e-commerce: аутентификация, каталог (категории, бренды, товары), листинг с фильтрами и сортировкой. Запуск в Docker.

## Stack

* **FastAPI** + **Uvicorn**
* **SQLAlchemy** + **Alembic** (PostgreSQL)
* **Redis** (зарезервировано под кеш/сессии)
* Docker / docker-compose

## 📂 Структура проекта E-commerce Core API

```
.
├── alembic/                # 🗂️ Миграции БД (управление схемой)
│   ├── env.py              # ⚙️ Настройка миграций (URL БД, metadata)
│   ├── README              # 📄 Краткая справка по Alembic
│   ├── script.py.mako      # 📝 Шаблон для новых миграций
│   └── versions/           # 📜 Конкретные миграции
│       └── 4d3a288ebf04_initial_schema.py
│
├── alembic.ini             # ⚙️ Конфигурация Alembic (URL БД, пути к версиям)
│
├── app/                    # 🧩 Основное приложение FastAPI
│   ├── api/                # 🌐 API-слой (эндпоинты и зависимости)
│   │   ├── deps.py         # 🔗 Общие зависимости (Depends)
│   │   ├── __init__.py
│   │   └── routers/        # 📡 Маршруты (разделены по модулям)
│   │       ├── admin_catalog.py # 🛠️ API для админки каталога
│   │       ├── auth.py         # 🔑 Авторизация/регистрация
│   │       ├── health.py       # ❤️ Health-check endpoint
│   │       ├── __init__.py
│   │       ├── products.py     # 📦 Товары
│   │       └── users.py        # 👤 Пользователи
│   │
│   ├── core/               # ⚙️ Базовые настройки проекта
│   │   ├── config.py       # 🛠️ Конфиги (env, настройки)
│   │   └── security.py     # 🔐 Безопасность (JWT, хеширование паролей)
│   │
│   ├── db.py               # 🗄️ Подключение к БД, SessionLocal
│   ├── __init__.py
│   ├── main.py             # 🚀 Точка входа (FastAPI app)
│   │
│   ├── models/             # 🧱 SQLAlchemy модели
│   │   ├── catalog.py      # 📦 Модель каталога товаров
│   │   ├── __init__.py
│   │   └── user.py         # 👤 Модель пользователя
│   │
│   └── schemas/            # 📜 Pydantic схемы
│       ├── catalog.py      # 📦 Схемы для каталога
│       ├── __init__.py
│       └── user.py         # 👤 Схемы для пользователей
│
├── dev-requirements.txt    # 🧪 Зависимости для разработки (тесты, линтеры)
├── docker/
│   └── api.Dockerfile      # 🐳 Dockerfile для сервиса API
│
├── docker-compose.override.yml # ⚙️ Локальные оверрайды для Docker Compose
├── docker-compose.yml          # 🐳 Основной docker-compose (API, БД, Redis и т.д.)
│
├── Makefile                # 📂 Удобные команды (make run, make lint, make test)
├── pyproject.toml           # 📦 Настройки проекта (ruff, black, pytest, deps)
├── README.md                # 📖 Документация к проекту
├── requirements.txt         # 📦 Основные зависимости
└── structure.txt            # 📝 Описание структуры (скорее всего авто-сгенерировано)


alembic/ → миграции и управление схемой БД.

app/ → основное приложение:

api/ → роуты и зависимости,

core/ → конфиги и безопасность,

db.py → подключение к базе,

models/ → модели SQLAlchemy,

schemas/ → Pydantic-схемы,

main.py → точка входа.

docker/ и compose-файлы → инфраструктура.

Makefile + pyproject.toml + pre-commit → удобные DevOps-инструменты.

requirements.txt → зависимости.
```

## Быстрый старт

```bash
# 1) Создай .env из примера
cp .env.example .env

# 2) (Опционально) Укажи свой UID/GID, чтобы права на файлы были корректны
# см. секцию "Переменные окружения"

# 3) Запуск
docker compose up --build
```

Доступы:

* API: [http://localhost:8000](http://localhost:8000)
* Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
* Health: [http://localhost:8000/health](http://localhost:8000/health)

## Переменные окружения

Файл `.env` (базовый набор):

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

# Для корректных прав внутри контейнера (особенно для alembic/versions)
UID=1000
GID=1000
```

> `UID`/`GID` подставь под своего пользователя (проверь командой `id -u` / `id -g`).
> В `docker-compose.yml` сервис `api` должен запускаться с `user: "${UID}:${GID}"`.

## Миграции

Автогенерация миграции по изменениям моделей и применение:

```bash
# создать миграцию из текущих моделей
docker compose exec api alembic revision -m "my change" --autogenerate

# применить все миграции
docker compose exec api alembic upgrade head

# посмотреть историю / текущую ревизию
docker compose exec api alembic history
docker compose exec api alembic current
```

### Чистый старт БД (полный ресет)

```bash
# остановить и удалить контейнеры
docker compose down

# удалить volume с данными Postgres
docker volume rm e-commerce_core_api_pgdata  # имя см. в `docker volume ls`

# поднять заново (создаст пустую БД)
docker compose up --build
```

## Аутентификация (JWT)

1. **Регистрация**: `POST /auth/register` — создаёт пользователя (is\_superuser=false).
2. **Логин**: `POST /auth/login` (`application/x-www-form-urlencoded`) — вернёт `access_token`.
3. Нажми **Authorize** в Swagger и вставь токен как `Bearer <access_token>`.
4. **Проверка**: `GET /users/me` вернёт данные текущего пользователя.

### Повышение до суперпользователя

Админ-эндпоинты каталога требуют `is_superuser=true`. В dev можно пометить пользователя напрямую в БД:

```bash
# войти в psql
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

# в psql:
UPDATE users SET is_superuser = true WHERE email = 'you@example.com';
```

## Каталог (admin)

Требует авторизации суперпользователя.

* **Категории**

  * `POST /admin/categories` — создать
  * `PATCH /admin/categories/{cat_id}` — обновить (частичное)
  * `DELETE /admin/categories/{cat_id}` — удалить
* **Бренды**

  * `POST /admin/brands`
  * `PATCH /admin/brands/{brand_id}`
  * `DELETE /admin/brands/{brand_id}`
* **Товары**

  * `POST /admin/products`
  * `PATCH /admin/products/{prod_id}`
  * `DELETE /admin/products/{prod_id}`

**Подсказки для PATCH**
Отправляй **только те поля**, которые меняешь.
`brand_id` и `category_id` должны ссылаться на **существующие** записи (иначе будет ошибка внешнего ключа).
Для уникальных полей (`sku`, `slug`) используй уникальные значения.

Примеры тел:

```json
// Создать товар
{
  "sku": "IPH14-128-BLK",
  "name": "iPhone 14 128GB Black",
  "slug": "iphone-14-128-black",
  "brand_id": 1,
  "category_id": 1,
  "price_cents": 700000,
  "is_active": true
}
```

```json
// Обновить товар (частично)
{
  "name": "iPhone 14 128GB Midnight",
  "slug": "iphone-14-128-midnight",
  "price_cents": 800000
}
```

## Публичный листинг товаров

`GET /products` — параметры:

* `q`: строка поиска по `name`/`slug`
* `category_id`: фильтр по категории
* `brand_id`: фильтр по бренду
* `sort`: `price_asc`, `price_desc`, `created_desc` (по умолчанию), `created_asc`
* `limit` (по умолчанию 20, максимум 100)
* `offset` (по умолчанию 0)

Ответ — обёртка с пэйджингом:

```json
{
  "total": 123,
  "limit": 20,
  "offset": 0,
  "items": [ { ...ProductRead }, ... ]
}
```

## Полезные команды

```bash
# Логи сервиса api
docker compose logs -f api

# Зайти в контейнер api
docker compose exec api bash

# Быстрая проверка таблиц в Postgres
docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

## Разработка

* Hot-reload включён (смонтированы `app/`, `alembic/`, `alembic.ini` в контейнер api).
* Соблюдаем линт: pre-commit с Ruff форматирует/проверяет код при коммите.

## Траблшутинг

* **403 Forbidden** на admin-эндпоинтах: текущий пользователь не `is_superuser=true`.
* **500 Internal Server Error** при PATCH/POST товаров:

  * конфликт уникальности `slug`/`sku` → используй другое значение;
  * неверные `brand_id`/`category_id` (несуществующие) → укажи корректные id.
* **Swagger /docs не открывается**:

  * проверь `docker compose ps` (api должен слушать `0.0.0.0:8000`);
  * убедись, что порт 8000 не занят локальным процессом.
