.PHONY: run up down logs lint fmt test

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f api

lint:
	ruff check .

fmt:
	ruff check . --fix; ruff format .

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

migrate:
	docker compose exec api alembic upgrade head

makemigration:
	docker compose exec api alembic revision -m "$(m)" --autogenerate

psql:
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB
