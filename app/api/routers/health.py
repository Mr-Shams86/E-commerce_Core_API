from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/healthz")
async def healthz():
    # здесь позже добавим реальные пинги к DB/Redis
    return {
        "status": "ok",
        "env": settings.app_env,
        "services": {
            "db": "unknown",
            "redis": "unknown",
        },
    }
