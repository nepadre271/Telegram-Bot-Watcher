from operator import attrgetter
import math
import copy

from aiogram_dialog import (
    DialogManager,
)
from dependency_injector.wiring import Provide, inject
from aiogram import types
from loguru import logger

from bot.dialogs.keyboards import get_next_page
from bot.settings import settings
from bot.utils import is_user_subscribed, check_admin_status
from core.repositories import UserRepository, SubscribeRepository
from bot.dialogs.const import MOVIES_LIMIT
from core.services import MovieService
from bot.containers import Container


@logger.catch()
@inject
async def movies_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service], **_kwargs):
    data = dialog_manager.start_data
    logger.debug(f"{dialog_manager.start_data=}")
    page = get_next_page(dialog_manager, _kwargs, prefix="m")
    
    search_result = data.get("data", None)
    if search_result is not None:
        search_result = copy.deepcopy(search_result)
        dialog_manager.start_data["data"] = None
    elif data.get("type", "") == "recommendations":
        search_result = await movie_service.recommendations(page=page, limit=MOVIES_LIMIT)
    else:
        search_result = await movie_service.search(data["query"], page=page, limit=MOVIES_LIMIT)
    
    movies = []
    if search_result is None:
        return {
            "movies": movies
        }

    dialog_manager.dialog_data["total_pages"] = math.ceil(search_result.total / 10)
    logger.debug(dialog_manager.dialog_data)
    for movie in search_result.movies:
        movie_data = {
            "title": f"{movie.name} ({'Сериал, ' if movie.is_series else ''}{movie.year})",
            "id": movie.id
        }
        if movie.can_download is False:
            movie_data["title"] = f"❌ {movie_data['title']}"
        movies.append(movie_data)

    return {
        "movies": movies,
    }


@logger.catch()
@inject
async def seasons_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service], **_kwargs):
    logger.debug(dialog_manager.dialog_data)
    movie_id = dialog_manager.dialog_data["movie_id"]
    movie = await movie_service.get(movie_id)

    if movie is None:
        return []

    seasons = [{"number": number, "title": season.title} for number, season in enumerate(movie.seasons, start=1)]

    return {
        "seasons": seasons
    }


@logger.catch()
@inject
async def serias_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service], **_kwargs):
    logger.debug(dialog_manager.dialog_data)
    movie_id = dialog_manager.dialog_data["movie_id"]
    season_number = dialog_manager.dialog_data["season_number"]
    movie = await movie_service.get(movie_id)

    if movie is None:
        return []

    season = movie.seasons[season_number-1]
    season.series.sort(key=attrgetter("number"))
    serias = [{"number": number, "title": seria.number} for number, seria in enumerate(season.series, start=1)]

    return {
        "serias": serias
    }


@logger.catch()
@inject
async def genres_getter(
        dialog_manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service],
        **_kwargs
):
    genres = await movie_service.get_genres()
    return {
        "genres": genres
    }


@inject
async def account_getter(
        dialog_manager: DialogManager,
        user_repository: UserRepository = Provide[Container.user_repository],
        **_kwargs
):
    text = []
    if isinstance(dialog_manager.event, types.Message):
        user_id = dialog_manager.event.chat.id
    else:
        user_id = dialog_manager.event.message.chat.id

    user = await user_repository.get(user_id)
    is_admin = check_admin_status(user)
    if is_admin:
        text.append("Статус: Администратор")

    user_sub_to_group = await is_user_subscribed(dialog_manager.event.bot, user_id, settings.chat_id)
    text.append(f"Подписка на группу: {'✔' if user_sub_to_group else '❌'}")
    text.append(f"Просмотров осталось: {'♾' if is_admin else user.views_left}")

    if is_admin:
        text.append(f"Подписка действительна до ♾")
    elif user.is_subscribe_expire() is False:
        text.append(f"Подписка действительна до {user.subscribe_expire.strftime('%d.%m.%Y %H:%M')} по мск")
    else:
        text.append(f"Подписка недействительна")

    invite_count = await user_repository.invites_count(user)
    text.append(f"Пользователей приглашено: {invite_count}")

    return {
        "text": "\n".join(text)
    }


@inject
async def subscribes_getter(
        dialog_manager: DialogManager,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
        **_kwargs
):
    subscribes = await subscribe_repository.all()
    logger.debug(f"{subscribes=}")
    return {
        "subscribes": subscribes
    }
