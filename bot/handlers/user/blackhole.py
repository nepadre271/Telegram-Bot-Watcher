from aiogram import Router, types
from loguru import logger


router = Router()


@router.message()
async def blackhole_handler(
        message: types.Message, flags={"skip_user_middleware": True}
):
    logger.info(f"BLACKHOLE: USER:{message.chat.id} MESSAGE: {message.text}")
