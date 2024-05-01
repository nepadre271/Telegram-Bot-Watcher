from redis.asyncio import Redis


class Storage:
    def __init__(self, redis: Redis, name: str):
        self.redis = redis
        self.name = name

    async def set(self, key: str | int, value: str):
        if isinstance(key, int):
            key = str(key)

        await self.redis.hset(self.name, key, value)
        
    async def get(self, key: str | int) -> str | None:
        if isinstance(key, int):
            key = str(key)

        return await self.redis.hget(self.name, key)
    
    async def delete(self, key: str | int):
        if isinstance(key, int):
            key = str(key)

        exists = await self.redis.hexists(self.name, key)
        if exists:
            await self.redis.hdel(self.name, key)


class Queue:
    def __init__(self, redis: Redis, name: str):
        self.redis = redis
        self.name = name
        
    async def add(self, prefix: str | int, value: str):
        await self.redis.rpush(f"{self.name}:{prefix}", value)
    
    async def pop(self, prefix: str | int) -> str:
        return await self.redis.lpop(f"{self.name}:{prefix}")
    
    async def length(self, prefix: str | int) -> int:
        return await self.redis.llen(f"{self.name}:{prefix}")
