from functools import lru_cache

from pydantic import BaseModel, Field

from core.schemes.movie.kinoclub import MovieType


class UploadMovieRequest(BaseModel):
    user_id: str | int = Field(...)
    movie_id: int = Field(...)
    type: MovieType = Field(...)
    file_id: str | None = Field(default=None)
    season: int | None = Field(default=None)
    seria: int | None = Field(default=None)

    def get_movie_id(self) -> str:
        @lru_cache()
        def wrapper():
            nonlocal self
            return "_".join(map(str, [self.movie_id, self.season, self.seria]))
        return wrapper()
