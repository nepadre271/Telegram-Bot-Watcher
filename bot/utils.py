from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot


async def is_user_subscribed(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except TelegramBadRequest:
        return False
