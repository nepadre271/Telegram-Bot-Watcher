from typing import AsyncIterator

from hishel._utils import generate_key
from redis.asyncio import Redis
import httpcore
import hishel


def _key_generator(request: httpcore.Request, body: bytes = b"") -> str:
    prefix = "CachedResponse"
    key = generate_key(request, body)
    return f"{prefix}:{key}"


def cache_client_factory(redis: Redis) -> hishel.AsyncCacheClient:
    # All the specification configs
    controller = hishel.Controller(
            # Cache only GET and POST methods
            cacheable_methods=["GET"],

            # Cache only 200 status codes
            cacheable_status_codes=[200],
            force_cache=True,
            key_generator=_key_generator
    )

    # All the storage configs
    storage = hishel.AsyncRedisStorage(
        client=redis,
        ttl=86400 * 31
    )
    client = hishel.AsyncCacheClient(controller=controller, storage=storage)
    return client


async def init_redis(redis_dsn: str) -> AsyncIterator[Redis]:
    redis = Redis.from_url(redis_dsn, encoding="utf-8", decode_responses=True)
    
    yield redis

    await redis.aclose()
