from typing import Callable, Dict, Any, Awaitable

from dependency_injector.wiring import Provide, inject
from aiogram.dispatcher.flags import get_flag
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
        skip = get_flag(data, "skip_user_middleware", default=False)
        user_obj = data.get("event_from_user", None)
        if user_obj is not None and skip is False:
            user = await user_repository.get(user_obj.id)
            data["user"] = user
            # Текущая сессия требуется в тех ситуациях когда нужно сохранить изменения модели User
            # полученной из middleware, передайте сессию в user_repository.session
            data["user_repository_session"] = user_repository.session

            if user_obj.username != user.username:
                await user_repository.update_username(user, user_obj.username)

        return await handler(event, data)
