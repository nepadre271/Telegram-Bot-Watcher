from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram import Bot

from uploader.settings import settings


def bot_factory() -> Bot:
    api_backend = TelegramAPIServer.from_base(settings.telegram_api, is_local=True)
    bot = Bot(token=settings.telegram_token, session=AiohttpSession(api=api_backend))
    return bot
