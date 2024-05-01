import hashlib

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dependency_injector.wiring import inject, Provide
from aiogram import Router, F, types
from redis.asyncio import Redis
from loguru import logger

from bot.keyboards.inline import create_movie_buttons
from bot.schemes import SelectMovieCallbackFactory, UploadMovieCallbackFactory
from core.services.movie import MovieService
from bot.containers import Container


router = Router()


@router.message(F.text.lower() == 'поиск по названию🔎')
async def search_by_name(message: types.Message):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Поиск по названию'")
    await message.answer("Введите название фильма или сериала, который вы хотите найти:")


@router.message()
@inject
async def get_search_results(
    message: types.Message, 
    redis: Redis = Provide[Container.redis_client],
    movie_service: MovieService = Provide[Container.movie_service]
):
    query = message.text
    logger.info(f"Пользователь {message.from_user.username} выбирает фильм по запросу '{query}'")
    try:
        results = await movie_service.search(query)
        if not results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        query_hash = hashlib.sha1(query.encode()).hexdigest()
        await redis.hset("query-table", query_hash, query)

        inline_kb = create_movie_buttons(results, query_hash)
        await message.answer("Выберите фильм или сериал из списка ниже:", reply_markup=inline_kb)

    except Exception as e:
        logger.error(f"Произошла ошибка при поиске: {str(e)}")
        await message.answer("Произошла ошибка при поиске. Пожалуйста, попробуйте еще раз.")
