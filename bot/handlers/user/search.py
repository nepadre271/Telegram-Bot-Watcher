import logging

from aiogram import Router, F, types

from bot.keyboards.inline import create_movie_buttons
from bot.settings import settings
from bot.api import KinoPoiskAPI

router = Router()
kp_api = KinoPoiskAPI(settings.kp_token)

logger = logging.getLogger(__name__)


@router.message(F.text.lower() == 'поиск по названию🔎')
async def search_by_name(message: types.Message):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Поиск по названию'")
    await message.answer("Введите название фильма или сериала, который вы хотите найти:")


@router.message()
async def get_search_results(message: types.Message):
    query = message.text
    logger.info(f"Пользователь {message.from_user.username} выбирает фильм по запросу '{query}'")
    try:
        results = await kp_api.search_movies(query)
        if not results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        inline_kb = create_movie_buttons(results, kp_api.current_index, len(kp_api.results))
        await message.answer("Выберите фильм или сериал из списка ниже:", reply_markup=inline_kb)

    except Exception as e:
        logger.error(f"Произошла ошибка при поиске: {str(e)}")
        await message.answer("Произошла ошибка при поиске. Пожалуйста, попробуйте еще раз.")
