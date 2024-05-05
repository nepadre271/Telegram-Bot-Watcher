from typing import AsyncIterator, Callable
import datetime

from hishel._serializers import Metadata
from hishel._utils import generate_key, float_seconds_to_int_milliseconds
from redis.asyncio import Redis
import httpcore
import hishel


def _key_generator(prefix: str = "") -> Callable:
    def inner(request: httpcore.Request, body: bytes = b"") -> str:
        nonlocal prefix
        start_prefix = "Response"
        key = generate_key(request, body)
        return f"{start_prefix}:{prefix}:{key}"
    return inner


class AsyncRedisStorage(hishel.AsyncRedisStorage):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def store(
            self, key: str, response: httpcore.Response,
            request: httpcore.Request, metadata: Metadata | None = None
    ) -> None:
        metadata = metadata or Metadata(
            cache_key=key, created_at=datetime.datetime.now(datetime.timezone.utc), number_of_uses=0
        )

        px = None
        for name, value in request.headers:
            if name == b"ttl":
                try:
                    px = float(value)
                except ValueError:
                    pass

        if px is not None:
            px = float_seconds_to_int_milliseconds(px)
        elif self._ttl is not None:
            px = float_seconds_to_int_milliseconds(self._ttl)

        await self._client.set(
            key, self._serializer.dumps(response=response, request=request, metadata=metadata), px=px
        )


def cache_client_factory(
        redis: Redis,
        base_url: str = "",
        ttl: int | None = 86400 * 31,
        force_cache: bool = True,
        key_prefix: str = ""
) -> hishel.AsyncCacheClient:
    # All the specification configs
    controller = hishel.Controller(
            # Cache only GET and POST methods
            cacheable_methods=["GET"],

            # Cache only 200 status codes
            cacheable_status_codes=[200],
            force_cache=force_cache,
            key_generator=_key_generator(key_prefix)
    )

    # All the storage configs
    storage = AsyncRedisStorage(
        client=redis,
        ttl=ttl
    )
    client = hishel.AsyncCacheClient(controller=controller, storage=storage, base_url=base_url)
    return client


async def init_redis(redis_dsn: str) -> AsyncIterator[Redis]:
    redis = Redis.from_url(redis_dsn, encoding="utf-8", decode_responses=True)

    yield redis

    await redis.aclose()
