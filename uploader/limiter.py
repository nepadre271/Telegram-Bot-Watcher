from datetime import datetime

from typing import Annotated, AsyncGenerator, Optional
from taskiq import Context, TaskiqDepends, TaskiqState
from redis.asyncio import ConnectionPool, Redis


def get_redis_pool(state: TaskiqState = TaskiqDepends()) -> ConnectionPool:
    return state.redis_pool


async def get_redis_connection(
    pool: ConnectionPool = TaskiqDepends(get_redis_pool),
) -> Redis:
    async with Redis(connection_pool=pool) as conn:
        yield conn


class ConcurencyLimiter:
    def __init__(self, counter_name: Optional[str] = None, limit: int = 2):
        self.limit = limit
        self.counter_name = f"{counter_name}.{datetime.now().second}"

    async def __call__(
        self,
        redis: Redis = TaskiqDepends(get_redis_connection),
        context:  Annotated[Context, TaskiqDepends()] = TaskiqDepends(),
    ) -> AsyncGenerator[None, None]:
        cur_val = int(await redis.get(self.counter_name) or 0)

        # If limit already reached we call requeue, to put it back in queue.
        if cur_val >= self.limit:
            await context.requeue()

        # You increase your counter before task execution.
        await redis.incr(self.counter_name)

        yield

        # You decrease it after the function is complete.
        await redis.decr(self.counter_name)
