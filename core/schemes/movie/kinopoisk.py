from pydantic import BaseModel, Field

from .base import MovieMin
    

class SearchResponse(BaseModel):
    movies: list[MovieMin] = Field(..., alias="docs")
    total: int = Field(...)
    limit: int = Field(...)
    page: int = Field(...)
    pages: int = Field(...)
    query: str | None = Field(default=None)
