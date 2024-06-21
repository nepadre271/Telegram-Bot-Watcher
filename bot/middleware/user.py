from typing import Callable, Dict, Any, Awaitable

from dependency_injector.wiring import Provide, inject
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware

from core.repositories import UserRepository
from bot.containers import Container


class UserMiddleware(BaseMiddleware):
    @inject
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
        user_repository: UserRepository = Provide[Container.user_repository]
    ) -> Any:
        skip = data.get("skip_user_middleware", False)
        user_obj = data.get("event_from_user", None)
        if user_obj is not None and skip is False:
            user = await user_repository.get(user_obj.id)
            data["user"] = user
        return await handler(event, data)
