from aiogram import Router, types
from loguru import logger

from bot.utils import tracker


router = Router()


@router.message(flags={"skip_user_middleware": True})
@tracker("Blackhole")
async def blackhole_handler(
        message: types.Message, **kwargs
):
    logger.info(f"BLACKHOLE: USER:{message.chat.id} MESSAGE: {message.text}")
