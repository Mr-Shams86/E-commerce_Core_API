FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# системные пакеты
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# deps
COPY requirements.txt /app/requirements.txt
COPY dev-requirements.txt /app/dev-requirements.txt
RUN python -m pip install --upgrade pip --no-cache-dir \
 && pip install --no-cache-dir -r /app/requirements.txt \
 && pip install --no-cache-dir -r /app/dev-requirements.txt

# код приложения
COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY tests /app/tests
COPY tests /app/tests


EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
