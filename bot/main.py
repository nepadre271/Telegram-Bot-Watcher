import logging
import asyncio

# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram import Bot, Dispatcher

# from bot.middleware.db import DbSessionMiddleware
from bot.settings import settings
from bot.handlers import user

logging.basicConfig(level=logging.INFO)
logging.getLogger('aiogram.event').setLevel(logging.CRITICAL)


def bot_factory() -> Bot:
    api_backend = TelegramAPIServer.from_base("http://telegram-bot-api:8081", is_local=True)
    bot = Bot(token=settings.tg_token, session=AiohttpSession(api=api_backend))
    return bot


async def main():
    # engine = create_async_engine(url=settings.db_url, echo=True)
    # sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    
    bot = bot_factory()
    dp = Dispatcher()

    dp.include_routers(*user.routes)
    # dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass
