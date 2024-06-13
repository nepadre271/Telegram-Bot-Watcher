from aiogram_dialog import DialogManager, StartMode
from dependency_injector.wiring import inject, Provide
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from loguru import logger

from core.services.movie import MovieService
from bot.dialogs.const import MOVIES_LIMIT
from bot.containers import Container
from bot.states import DialogSG, DialogSelectGenres


router = Router()


@router.message(F.text.lower() == 'поиск по названию🔎')
async def search_by_name(message: types.Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Поиск по названию'")
    await message.answer("Введите название фильма или сериала, который вы хотите найти:")
    await state.set_state(DialogSG.WAIT_NAME_INPUT)


@router.message(F.text.lower() == 'по жанрам')
async def search_by_genre(message: types.Message, dialog_manager: DialogManager):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Поиск по жанрам'")
    await dialog_manager.start(
        DialogSelectGenres.SELECT_GENRE, mode=StartMode.RESET_STACK
    )


@router.message(F.text.lower() == 'рекомендации')
@logger.catch()
@inject
async def search_by_recommendation(
        message: types.Message,
        dialog_manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service]
):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Рекомендации'")
    results = await movie_service.recommendations(limit=MOVIES_LIMIT)
    if not results:
        await message.answer("К сожалению, по вашему запросу ничего не найдено.")
        return

    await dialog_manager.start(
        DialogSG.SELECT_MOVIE, mode=StartMode.RESET_STACK,
        data={"type": "recommendations", "data": results}
    )


@router.message(StateFilter(DialogSG.WAIT_NAME_INPUT))
@logger.catch()
@inject
async def get_search_results(
        message: types.Message,
        dialog_manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service]
):
    query = message.text
    logger.info(f"Пользователь {message.from_user.username} выбирает фильм по запросу '{query}'")
    results = await movie_service.search(query, limit=MOVIES_LIMIT)
    if not results:
        await message.answer("К сожалению, по вашему запросу ничего не найдено.")
        return

    await dialog_manager.start(
        DialogSG.SELECT_MOVIE, mode=StartMode.RESET_STACK,
        data={"query": query, "data": results}
    )
