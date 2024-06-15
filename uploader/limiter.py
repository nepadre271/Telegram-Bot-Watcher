from functools import wraps
import asyncio

from taskiq import Context


def concurrency_limiter_handler(limit_per_worker: int = 2):
    semaphore = asyncio.Semaphore(limit_per_worker)

    def inner(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal semaphore
            context: Context = kwargs.get("context")

            if semaphore.locked():
                await context.requeue()

            await semaphore.acquire()
            try:
                result = await func(*args, **kwargs)
            finally:
                semaphore.release()

            return result

        return wrapper

    return inner