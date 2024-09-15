import asyncio
import socket

from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from dependency_injector.wiring import Provide, inject
from aiogram.client.telegram import TelegramAPIServer
from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher

from bot.containers import Container
from bot.payment import BaseSubscribePayment
from bot.settings import settings
from bot.dialogs import windows
from bot.logger import logger
from bot import handlers, middleware


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
    container.config.yoomoney_token.from_value(settings.payment.yoomoney_token)
    container.config.payment.type.from_value(settings.payment.service)
    container.wire(
        modules=[__name__]
    )


@inject
async def init_bot(
        payment: BaseSubscribePayment = Provide[Container.payment]
):
    bot = bot_factory()

    storage = RedisStorage.from_url(
        url=settings.redis_dsn,
        connection_kwargs=dict(encoding="utf-8", decode_responses=True),
        key_builder=DefaultKeyBuilder(with_destiny=True)
    )

    dp = Dispatcher(storage=storage)

    dp.include_routers(*handlers.admin.routes)
    dp.include_routers(*handlers.user.routes)
    payment.registry_router(dp)

    dp.include_router(windows.video_select_dialog)
    dp.include_router(windows.genres_select_dialog)
    dp.include_router(windows.account_dialog)
    dp.include_router(windows.admin_dialog)

    dp.include_router(handlers.user.blackhole.router)
    setup_dialogs(dp)

    dp.message.middleware.register(middleware.UserMiddleware())
    dp.callback_query.middleware.register(middleware.UserMiddleware())

    dp.message.middleware.register(middleware.AdminMiddleware())
    dp.callback_query.middleware.register(middleware.AdminMiddleware())

    windows.admin_dialog.message.middleware.register(middleware.OnlyAdminMiddleware())
    windows.admin_dialog.callback_query.middleware.register(middleware.OnlyAdminMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass


@logger.catch()
async def main():
    init_container()
    await init_bot()
