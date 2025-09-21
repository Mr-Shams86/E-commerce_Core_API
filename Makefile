# =========
# Makefile
# =========
.DEFAULT_GOAL := help
.PHONY: help up upd down logs restart api-shell run lint fmt test install dev-install \
        migrate makemigration history downgrade-base downgrade-one clean psql

## Показать список команд
help:
	@echo "Available targets:" && \
	awk 'BEGIN{FS=":.*?## "} /^[a-zA-Z0-9_-]+:.*?## /{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

## Собрать и запустить docker-compose в фоне
upd:
	docker compose up --build -d

## Собрать и запустить docker-compose (в форграунде)
up:
	docker compose up --build

## Остановить и удалить контейнеры + тома
down:
	docker compose down -v

## Хвост логов API
logs:
	docker compose logs -f api

## Перезапустить только сервис api
restart:
	docker compose restart api

## Войти в контейнер API (bash)
api-shell:
	docker compose exec api bash

## Локальный запуск без Docker (dev)
run:
	uvicorn app.main:app --reload --port 8000

## Линтинг (ruff)
lint:
	ruff check .

## Автофиксы + форматирование (ruff)
fmt:
	ruff check . --fix ; ruff format .

## Тесты
test:
	pytest -q

	\tdocker compose exec api pytest -q -o cache_dir=/tmp/pytest_cache

## Установить runtime-зависимости
install:
	pip install -r requirements.txt

## Установить dev-зависимости
dev-install:
	pip install -r dev-requirements.txt

## Применить миграции до head
migrate:                     ## alembic upgrade head (в контейнере)
	docker compose exec api alembic upgrade head

## Создать ревизию: make makemigration m="create users table"
makemigration:               ## alembic revision --autogenerate -m "<msg>"
	docker compose exec api alembic revision -m "$(m)" --autogenerate

## История миграций
history:
	docker compose exec api alembic history

## Откат ко всем нулевым миграциям
downgrade-base:
	docker compose exec api alembic downgrade base

## Откат на одну миграцию назад
downgrade-one:
	docker compose exec api alembic downgrade -1

## Подключиться к psql в контейнере БД
psql:
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

## Почистить кэш/мусор
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + ; \
	find . -type f -name "*.pyc" -delete

## Подключиться к psql в контейнере БД (вариант 2)
psql:
	docker compose exec db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'
