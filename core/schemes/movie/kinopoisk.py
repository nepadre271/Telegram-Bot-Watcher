from pydantic import BaseModel, Field, TypeAdapter

from .base import MovieMin
    

class SearchResponse(BaseModel):
    movies: list[MovieMin] = Field(..., alias="docs")
    total: int = Field(...)
    limit: int = Field(...)
    page: int = Field(...)
    pages: int = Field(...)


class Genre(BaseModel):
    name: str = Field(...)
    slug: str = Field(...)


genres_list_adapter = TypeAdapter(list[Genre])
