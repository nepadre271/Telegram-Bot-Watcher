from functools import wraps

from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot

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
    async def wrapper(
            *args, **kwargs
    ):
        is_admin = kwargs.get("is_admin", False)

        if is_admin:
            return await func(*args, **kwargs)
        return
    return wrapper
