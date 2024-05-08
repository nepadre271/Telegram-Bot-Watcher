from core.repositories.movie import MovieRepository
from core.schemes.movie import kinoclub, kinopoisk


class MovieService:
    def __init__(self, movie_repository: MovieRepository):
        self.repository = movie_repository
    
    async def get(self, movie_id: int, disable_cache: bool = False) -> kinoclub.Movie | None:
        return await self.repository.get_movie(movie_id, disable_cache=disable_cache)
    
    async def search(self, query: str | dict, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        return await self.repository.search(query, page, limit)

    async def recommendations(self, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        return await self.repository.recommendations(page, limit)

    async def get_genres(self) -> list[kinopoisk.Genre]:
        return await self.repository.get_genres()
