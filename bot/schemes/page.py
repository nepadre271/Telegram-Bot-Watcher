from aiogram.filters.callback_data import CallbackData
from pydantic import Field, PositiveInt


class PageCallbackFactory(CallbackData, prefix="p"):
    number: PositiveInt = Field(...)
    query_hash: str = Field(...)
