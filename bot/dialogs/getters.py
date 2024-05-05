from operator import attrgetter
import math

from aiogram_dialog import (
    DialogManager,
)
from dependency_injector.wiring import Provide, inject
from loguru import logger

from core.services import MovieService
from bot.containers import Container
from bot.dialogs.const import MOVIES_LIMIT, SEASONS_LIMIT, SERIAS_LIMIT


@logger.catch()
@inject
async def movies_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service], **_kwargs):
    data = dialog_manager.start_data

    logger.debug(dialog_manager.dialog_data)
    page = get_next_page(dialog_manager, _kwargs, prefix="m")
    search_result = await movie_service.search(data["query"], page=page, limit=MOVIES_LIMIT)

    movies = []
    if search_result is None:
        return movies

    dialog_manager.dialog_data["total_pages"] = math.ceil(search_result.total / 10)
    logger.debug(dialog_manager.dialog_data)
    for movie in search_result.movies:
        movies.append({
            "title": f"{movie.name} ({'Сериал, ' if movie.is_series else ''}{movie.year})",
            "id": movie.id
        })

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


def get_next_page(dialog_manager: DialogManager, data: dict, prefix: str) -> int:
    pager_data = data.get("aiogd_original_callback_data", "")
    page = dialog_manager.dialog_data.get("page", 1)

    if f"{prefix}_pager_next" in pager_data:
        page = page + 1
    elif f"{prefix}_pager_prev" in pager_data:
        page = page - 1

    dialog_manager.dialog_data["page"] = page
    return page
