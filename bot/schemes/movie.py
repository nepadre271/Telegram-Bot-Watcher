from aiogram.filters.callback_data import CallbackData
from pydantic import Field


class UploadMovieCallbackFactory(CallbackData, prefix="up"):
    id: int = Field(...)
    season: int | None = Field(None)
    seria: int | None = Field(None)


class SelectMovieCallbackFactory(CallbackData, prefix="select"):
    id: int = Field(...)

