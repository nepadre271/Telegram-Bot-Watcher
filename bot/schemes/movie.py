from enum import Enum

from pydantic import BaseModel, Field, AnyHttpUrl


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
    number: str = Field(...)
    download_url: AnyHttpUrl = Field(..., alias="url")


class Season(BaseModel):
    title: str = Field(...)
    series: list[Seria] = Field(...)


class Movie(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
    type: MovieType | str = Field(...)
    full_description: str = Field(...)
    short_description: str = Field(..., alias="description")
    poster: AnyHttpUrl = Field(...)
    seasons: list[Season] = Field(default_factory=list)
    download_url: AnyHttpUrl | None = Field(default=None, alias="url")
