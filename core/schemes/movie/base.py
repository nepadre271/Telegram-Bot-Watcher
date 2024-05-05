from pydantic import BaseModel, Field


class MovieMin(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    year: int | str | None = Field(default=None)
    is_series: bool = Field(default=False, alias="isSeries")
