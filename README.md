# E-commerce Core API (FastAPI)

## Run
```bash
cp .env.example .env
docker compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health

### Миграции
```bash
docker compose exec api alembic revision -m "..." --autogenerate
docker compose exec api alembic upgrade head
