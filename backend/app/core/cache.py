import redis
from app.core.config import get_settings

settings = get_settings()
cache = redis.Redis.from_url(settings.redis_url, decode_responses=True)
