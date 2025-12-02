import time

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.deps import get_db
from app.core.cache import get_redis
from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/healthz")
async def healthz(db=Depends(get_db)):
    db_status = "Unknown"
    redis_status = "Unknown"

    # DB check
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    start = time.monotonic()

    # Redis check
    try:
        redis = get_redis()
        redis.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    latency_ms = round((time.monotonic() - start) * 1000, 2)

    return {
        "status": "ok",
        "env": settings.app_env,
        "latency_ms": latency_ms,
        "services": {
            "db": db_status,
            "redis": redis_status,
        },
    }
