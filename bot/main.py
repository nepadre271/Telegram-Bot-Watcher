import asyncio
import socket

from aiogram.client.session.aiohttp import AiohttpSession
from dependency_injector.wiring import Provide, inject
from aiogram.client.telegram import TelegramAPIServer
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from bot.dialogs.windows import dialog
from bot.containers import Container
from bot.settings import settings
from bot.handlers import user
from bot.logger import logger


def bot_factory() -> Bot:
    session = None

    try:
        if socket.gethostbyname("telegram-bot-api"):
            api_backend = TelegramAPIServer.from_base("http://telegram-bot-api:8081", is_local=True)
            session = AiohttpSession(api=api_backend)
    except socket.gaierror:
        pass

    bot = Bot(token=settings.tg_token, session=session)
    return bot


def init_container():
    container = Container()
    container.config.redis_dsn.from_value(settings.redis_dsn)
    container.config.uploader_url.from_value(settings.uploader_url)
    container.config.kinopoisk_token.from_value(settings.kinopoisk_token)
    container.config.kinoclub_token.from_value(settings.kinoclub_token)
    container.wire(
        modules=[__name__]
    )


async def init_bot():
    bot = bot_factory()

    # redis = Redis.from_url(url=settings.redis_dsn, encoding="utf-8", decode_responses=True)
    # storage = RedisStorage(redis=redis)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(dialog)
    setup_dialogs(dp)

    dp.include_routers(*user.routes)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass


@logger.catch()
async def main():
    init_container()
    await init_bot()
