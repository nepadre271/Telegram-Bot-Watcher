from aiogram_dialog import DialogManager, StartMode
from dependency_injector.wiring import inject, Provide
from aiogram import Router, F, types
from loguru import logger

from core.services.movie import MovieService
from bot.dialogs.const import MOVIES_LIMIT
from bot.dialogs.states import DialogSG
from bot.containers import Container


router = Router()


@router.message(F.text.lower() == 'поиск по названию🔎')
async def search_by_name(message: types.Message):
    logger.info(f"Пользователь {message.from_user.username} вызвал 'Поиск по названию'")
    await message.answer("Введите название фильма или сериала, который вы хотите найти:")


@router.message()
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
