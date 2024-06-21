from typing import Callable, Dict, Any, Awaitable

from aiogram.types import TelegramObject
from aiogram import BaseMiddleware

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
