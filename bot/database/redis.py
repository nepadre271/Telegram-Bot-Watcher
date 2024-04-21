from redis.asyncio import Redis, from_url
from bot.settings import settings

redis: Redis = from_url(settings.redis_dsn, decode_responses=True)
