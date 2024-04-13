import logging

import aiohttp

from bot.schemes import movie

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KinoPoiskAPI:
    BASE_URL = "https://api.kinopoisk.dev/"
    SEARCH_ENDPOINT = "v1.4/movie/search"

    def __init__(self, token: str):
        self.token = token
        self.results = []
        self.current_index = 0

    async def search_movies(self, query: str) -> list[dict]:
        self.results = []
        url = f"{self.BASE_URL}{self.SEARCH_ENDPOINT}"
        params = {"page": 1, "limit": 50, "query": query}
        headers = {"X-API-KEY": self.token}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    logger.warning(f"Запрос к {url} вернул код статуса {response.status}")
                    return self.results

                json_response = await response.json()
                self.results = json_response.get("docs", [])
                logger.info(f"Получено {len(self.results)} результатов по запросу '{query}'")

        return self.results[self.current_index: self.current_index + 10]


class KinoClubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://kinoclub.dev/api/movies/"

    async def get_movie(self, kp_id) -> movie.Movie | None:
        url = f"{self.base_url}{kp_id}"
        headers = {"Authorization": self.token}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None

                body = await response.json()
                if body.get("status", "") != "ok":
                    return None

                try:
                    result = movie.Movie.model_validate(body["data"])
                except ValueError:
                    return None
                else:
                    return result
