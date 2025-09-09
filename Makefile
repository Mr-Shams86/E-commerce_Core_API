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
