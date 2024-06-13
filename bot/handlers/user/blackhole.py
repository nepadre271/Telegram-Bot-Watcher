from aiogram import Router, types
from loguru import logger


router = Router()


@router.message()
async def blackhole_handler(
        message: types.Message
):
    logger.info(f"BLACKHOLE: USER:{message.chat.id} MESSAGE: {message.text}")
