from core.repositories.movie import MovieRepository
from core.schemes.movie import kinoclub, kinopoisk


class MovieService:
    def __init__(self, movie_repository: MovieRepository):
        self.repository = movie_repository
    
    async def get(self, movie_id: int) -> kinoclub.Movie | None:
        return await self.repository.get_movie(movie_id)
    
    async def search(self, query: str, page: int = 1, limit: int = 10) -> kinopoisk.SearchResponse | None:
        return await self.repository.search(query, page, limit)
