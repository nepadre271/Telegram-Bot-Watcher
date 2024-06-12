import asyncio
import socket

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher

from bot.containers import Container
from bot.settings import settings
from bot.dialogs import windows
from bot.handlers import user
from bot.logger import logger


def bot_factory() -> Bot:
    session = None

    try:
        if socket.gethostbyname("telegram-bot-api"):
            api_backend = TelegramAPIServer.from_base(settings.telegram.api, is_local=True)
            session = AiohttpSession(api=api_backend)
    except socket.gaierror:
        pass

    bot = Bot(token=settings.telegram.token, session=session)
    return bot


def init_container():
    container = Container()
    container.config.redis_dsn.from_value(settings.redis_dsn)
    container.config.database_dsn.from_value(settings.database_dsn)

    container.config.uploader_url.from_value(settings.uploader_url)
    container.config.kinopoisk_token.from_value(settings.kinopoisk_token)
    container.config.kinoclub_token.from_value(settings.kinoclub_token)
    container.wire(
        modules=[__name__]
    )


async def init_bot():
    bot = bot_factory()

    storage = RedisStorage.from_url(
        url=settings.redis_dsn,
        connection_kwargs=dict(encoding="utf-8", decode_responses=True),
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )

    dp = Dispatcher(storage=storage)
    dp.include_routers(*user.routes)

    dp.include_router(windows.video_select_dialog)
    dp.include_router(windows.genres_select_dialog)
    dp.include_router(windows.account_dialog)
    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass


@logger.catch()
async def main():
    init_container()
    await init_bot()
