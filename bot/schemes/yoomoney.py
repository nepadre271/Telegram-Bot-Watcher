from aiogram.filters.callback_data import CallbackData
from pydantic import Field


class YooMoneySubscribeCallbackFactory(CallbackData, prefix="yoo"):
    label: str = Field(...)
    sub_id: int = Field(...)
