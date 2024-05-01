from pydantic import ValidationError
from redis.asyncio import Redis
from loguru import logger

from core.schemes.movie import kinoclub, kinopoisk
from core.cache import cache_client_factory


class KinoClubAPI:
    BASE_URL = "https://kinoclub.dev/api/movies"
    
    def __init__(self, token: str, redis: Redis):
        self.token = token
        self.headers = {"Authorization": self.token}
        self.client = cache_client_factory(redis)
    
    async def get_movie(self, movie_id: int) -> kinoclub.Movie | None:
        url = f"{self.BASE_URL}/{movie_id}"
        headers = self.headers | {"cache-control": f"max-age={86400 * 31}"}
        response = await self.client.get(url, headers=headers)
        
        logger.debug(f"Response[{url}] from cache[{response.extensions['from_cache']}]")
        if response.status_code != 200:
            return None

        body = response.json()
        if body.get("status", "") != "ok":
            return None

        try:
            result = kinoclub.Movie.model_validate(body["data"])
        except ValueError as ex:
            logger.error(ex)
            return None
        else:
            return result


class KinoPoiskAPI:
    BASE_URL = "https://api.kinopoisk.dev/v1.4"

    def __init__(self, token: str, redis: Redis):
        self.token = token
        self.headers = {"X-API-KEY": self.token}
        self.client = cache_client_factory(redis)

    async def search_movies(self, query: str, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        url = f"{self.BASE_URL}/movie/search"
        params = {"page": page, "limit": limit, "query": query}
        headers = self.headers | {"cache-control": f"max-age={86400 * 31}"}
        
        response = await self.client.get(url, params=params, headers=headers)
        logger.debug(f"Response[{url} : {params=}] from cache[{response.extensions['from_cache']}]", )
        
        if response.status_code != 200:
            logger.warning(f"[{url}] вернул код статуса {response.status_code}; Body:{response.text}")
            return None

        data: bytes = response.read()
        
        try:
            result = kinopoisk.SearchResponse.model_validate_json(data)
            if result.query is None:
                result.query = query
        except (ValueError, ValidationError) as ex:
            logger.error(ex)
            return None

        return result


class MovieRepository:
    def __init__(self, kinopoisk_api: KinoPoiskAPI, kinoclub_api: KinoClubAPI):
        self.kinoclub = kinoclub_api
        self.kinopoisk = kinopoisk_api
        
    async def get_movie(self, movie_id: int) -> kinoclub.Movie | None:
        return await self.kinoclub.get_movie(movie_id)
    
    async def search(self, query: str, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        return await self.kinopoisk.search_movies(query, page, limit)
