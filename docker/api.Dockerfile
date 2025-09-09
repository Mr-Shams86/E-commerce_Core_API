FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# системные пакеты (build-essential может не понадобиться, но пусть будет для будущих либ)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# ставим зависимости отдельно — чтобы кэшировалось
COPY pyproject.toml /app/pyproject.toml
RUN pip install --upgrade pip \
 && pip install --no-cache-dir \
    "uvicorn[standard]" "fastapi" "pydantic-settings" "psycopg[binary]" "redis" "python-json-logger"

# код приложения
COPY app /app/app

# (не обязательно) EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
