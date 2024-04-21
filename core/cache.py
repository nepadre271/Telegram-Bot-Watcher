import sys

from redis.asyncio import Redis
from loguru import logger
import hishel

logger.add(sys.stdout, backtrace=True, diagnose=True)

@logger.catch
def cache_client_factory(redis: Redis) -> hishel.AsyncCacheClient:
    # All the specification configs
    controller = hishel.Controller(
            # Cache only GET and POST methods
            cacheable_methods=["GET"],

            # Cache only 200 status codes
            cacheable_status_codes=[200],
            force_cache=True
    )

    # All the storage configs
    storage = hishel.AsyncRedisStorage(
        client=redis,
        ttl=86400 * 31
    )
    client = hishel.AsyncCacheClient(controller=controller, storage=storage)
    return client
