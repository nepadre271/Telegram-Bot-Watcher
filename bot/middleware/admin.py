from typing import Callable, Dict, Any, Awaitable

from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from loguru import logger

from bot.utils import check_admin_status


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("user", None)
        if user is not None:
            data["is_admin"] = check_admin_status(user)
        return await handler(event, data)


class OnlyAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        is_admin = data.get("is_admin", False)
        if is_admin:
            return await handler(event, data)

