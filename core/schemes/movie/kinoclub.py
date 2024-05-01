from operator import attrgetter
from enum import Enum

from pydantic import BaseModel, Field, AnyHttpUrl, ConfigDict, field_validator

from .base import MovieMin


class MovieType(str, Enum):
    FILM = "film"
    SERIAL = "serial"

    @property
    def verbose(self) -> str:
        name_to_verbose = {
            "film": "Фильм",
            "serial": "Сериал"
        }
        return name_to_verbose.get(self.value, "")


class Seria(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    number: int = Field(..., alias="seria")
    download_url: AnyHttpUrl = Field(..., alias="url")

    @field_validator("number", mode="before")
    def validate_number(cls, value: str | int) -> int:
        if isinstance(value, str):
            return int(value)
        return value


class Season(BaseModel):
    title: str = Field(...)
    series: list[Seria] = Field(...)


class Movie(MovieMin):
    type: MovieType = Field(...)
    short_description: str = Field(..., alias="description")
    full_description: str = Field(...)
    poster: AnyHttpUrl = Field(...)
    seasons: list[Season] = Field(default_factory=list)
    download_url: AnyHttpUrl | None = Field(default=None, alias="url")

    def get_seria(self, season: int, seria: int) -> Seria:
        season: Season = self.seasons[season-1]
        season.series.sort(key=attrgetter("number"))
        return season.series[seria-1]
