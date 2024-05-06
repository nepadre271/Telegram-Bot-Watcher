from pydantic import ValidationError
from redis.asyncio import Redis
from loguru import logger

from core.schemes.movie import kinoclub, kinopoisk
from core.cache import cache_client_factory


class KinoClubAPI:
    def __init__(self, token: str, redis: Redis):
        self.token = token
        self.headers = {"Authorization": self.token}
        self.client = cache_client_factory(redis, "https://kinoclub.dev", key_prefix="KinoClub")
        
        self.redis = redis
        self.cache_table = "KinoClub:movies"
        
    async def get_available_movies_id(self) -> list[int]:
        url = "/films.json"
        response = await self.client.get(url)

        if response.status_code != 200:
            return []

        return response.json()
        
    async def update_available_movies_id(self):
        update = await self.redis.ttl(f"{self.cache_table}:update")
        table_exists = await self.redis.exists(self.cache_table)
        if update != -2 and table_exists:
            return
        
        movies_id = await self.get_available_movies_id()
        ids = {str(movie_id): "1" for movie_id in movies_id}
        await self.redis.hset(self.cache_table, mapping=ids)
        await self.redis.set(f"{self.cache_table}:update", "1", ex=86400 * 31)

    async def is_movie_exists(self, movie_id: int) -> bool:        
        exists = await self.redis.hexists(self.cache_table, str(movie_id))
        return exists

    async def get_movie(self, movie_id: int, disable_cache: bool = False) -> kinoclub.Movie | None:
        url = f"/api/movies/{movie_id}"
        response = await self.client.get(
            url, headers=self.headers,
            extensions={"cache_disabled": True, "force_cache": False} if disable_cache else {}
        )
        logger.debug(
            f"Response[{url}] from cache[{response.extensions.get('from_cache', False)}], "
            f"uses: {response.extensions.get('cache_metadata', {}).get('number_of_uses', 0)}"
        )
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

    def __init__(self, token: str, redis: Redis):
        self.token = token
        self.headers = {"X-API-KEY": self.token}
        self.client = cache_client_factory(redis, "https://api.kinopoisk.dev/v1.4", key_prefix="KinoPoisk")

    async def search_movies(self, query: str, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        url = f"/movie/search"
        params = {"page": page, "limit": limit, "query": query}

        response = await self.client.get(url, params=params, headers=self.headers)
        logger.debug(
            f"Response[{url}] from cache[{response.extensions.get('from_cache', False)}], "
            f"uses: {response.extensions.get('cache_metadata', {}).get('number_of_uses', 0)}"
        )

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

    async def get_movie(self, movie_id: int, disable_cache: bool = False) -> kinoclub.Movie | None:
        await self.kinoclub.update_available_movies_id()
        exists = await self.kinoclub.is_movie_exists(movie_id)
        if exists is False:
            return None
        return await self.kinoclub.get_movie(movie_id, disable_cache=disable_cache)

    async def search(self, query: str, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        data = await self.kinopoisk.search_movies(query, page, limit)
        
        await self.kinoclub.update_available_movies_id()
        for movie in data.movies:
            movie.can_download = await self.kinoclub.is_movie_exists(movie.id)
        
        return data
