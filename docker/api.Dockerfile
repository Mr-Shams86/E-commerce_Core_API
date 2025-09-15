FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# системные пакеты (build-essential может не понадобиться)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# ставим зависимости отдельно — чтобы кэшировалось
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip --no-cache-dir \
 && pip install --no-cache-dir -r /app/requirements.txt

# код приложения
COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic


# нерутовый пользователь
RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
