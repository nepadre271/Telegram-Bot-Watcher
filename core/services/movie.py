from redis.asyncio import Redis
import httpx

from core.schemes.movie import Movie
from core.cache import cache_client_factory
import sys

from redis.asyncio import Redis
from loguru import logger

logger.add(sys.stdout, backtrace=True, diagnose=True)


class KinoClubAPI:
    def __init__(self, token: str, redis: Redis):
        self.token = token
        self.headers = {"Authorization": self.token}
        self.base_url = "https://kinoclub.dev/api/movies/"
        self.client = cache_client_factory(redis)
    
    @logger.catch
    async def get_movie(self, movie_id) -> Movie | None:
        url = f"{self.base_url}{movie_id}"
        header = self.headers
        header["cache-control"] = f"max-age={86400 * 31}"
        response = await self.client.get(url, headers=self.headers)
        logger.info(f"Response[{url}] from cache[{response.extensions['from_cache']}]", )
        if response.status_code != 200:
            return None

        body = response.json()
        if body.get("status", "") != "ok":
            return None

        try:
            result = Movie.model_validate(body["data"])
        except ValueError as ex:
            logger.error(ex)
            return None
        else:
            return result
        

class UploaderService:
    def __init__(self, uploader_url: str):
        self.url = uploader_url
        
    async def upload_movie(self, chat_id: str, movie_id: int) -> int:
        async with httpx.AsyncClient(base_url=self.url) as client:
            response = await client.post("/upload", json={"user_id": str(chat_id), "movie_id": movie_id})
            return response.status_code
