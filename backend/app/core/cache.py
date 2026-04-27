import redis
from loguru import logger
from app.core.config import get_settings

settings = get_settings()


class _NoopCache:
    """Fallback in-memory no-op cache when Redis is unavailable."""

    def __init__(self):
        self._store: dict = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value, ex: int = 3600):
        self._store[key] = value

    def delete(self, key: str):
        self._store.pop(key, None)


def _build_cache():
    try:
        client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        logger.info("Redis cache connected at {}", settings.redis_url)
        return client
    except Exception as exc:
        logger.warning("Redis unavailable ({}). Using in-memory fallback cache.", exc)
        return _NoopCache()


cache = _build_cache()
