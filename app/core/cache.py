import redis

from app.core.config import settings

_redis = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> redis.Redis:
    return _redis
