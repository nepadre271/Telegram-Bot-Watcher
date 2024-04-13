import logging
import asyncio

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram import Bot, Dispatcher

from bot.settings import settings
from bot.handlers import user

logging.basicConfig(level=logging.INFO)
logging.getLogger('aiogram.event').setLevel(logging.CRITICAL)


async def main():
    api_backend = TelegramAPIServer.from_base("http://telegram-bot-api:8081", is_local=True)

    bot = Bot(token=settings.tg_token, session=AiohttpSession(api=api_backend))
    dp = Dispatcher()

    dp.include_routers(*user.routes)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        pass
