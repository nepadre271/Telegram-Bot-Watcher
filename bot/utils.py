from functools import wraps

from dependency_injector.wiring import Provide, inject
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram import Bot

from core.repositories import UserRepository
from bot.containers import Container
from bot.database.models import User
from bot.settings import settings


async def is_user_subscribed(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except TelegramBadRequest:
        return False


def check_admin_status(user: User) -> bool:
    return any([
        user.id in settings.telegram.admins,
        user.is_admin,
    ])


def only_admin_handler(func):
    @wraps(func)
    @inject
    async def wrapper(
            *args, user_repository: UserRepository = Provide[Container.user_repository], **kwargs
    ):
        message: Message = args[0]
        user = await user_repository.get(message.chat.id)

        if check_admin_status(user):
            kwargs["user_repository"] = user_repository
            return await func(*args, **kwargs)
        return
    return wrapper
