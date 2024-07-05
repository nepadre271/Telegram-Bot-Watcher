from operator import attrgetter
import math
import copy

from aiogram_dialog import (
    DialogManager,
)
from dependency_injector.wiring import Provide, inject
from loguru import logger

from core.repositories import UserRepository, SubscribeRepository
from bot.utils import is_user_subscribed, tracker
from bot.dialogs.keyboards import get_next_page
from bot.dialogs.const import MOVIES_LIMIT
from core.services import MovieService
from bot.containers import Container
from bot.settings import settings
from bot import states, schemes


@tracker("Movie_getter: show movie menu")
@logger.catch()
@inject
async def movies_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service],
                        **_kwargs):
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


@tracker("Movie_getter: show seasons menu")
@logger.catch()
@inject
async def seasons_getter(dialog_manager: DialogManager, movie_service: MovieService = Provide[Container.movie_service],
                         **_kwargs):
    logger.debug(dialog_manager.dialog_data)
    if _id := dialog_manager.start_data.get("movie_id", None):
        movie_id = _id
    else:
        movie_id = dialog_manager.dialog_data.get("movie_id", None)
    movie = await movie_service.get(movie_id)

    if movie is None:
        return {
            "seasons": []
        }

    seasons = [{"number": number, "title": season.title} for number, season in enumerate(movie.seasons, start=1)]

    return {
        "seasons": seasons
    }


@tracker("Movie_getter: show serias menu")
@logger.catch()
@inject
async def serias_getter(
        dialog_manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service],
        **_kwargs
):
    logger.debug(dialog_manager.dialog_data)
    movie_id = dialog_manager.dialog_data["movie_id"]
    season_number = dialog_manager.dialog_data["season_number"]
    movie = await movie_service.get(movie_id)

    if movie is None:
        return []

    season = movie.seasons[season_number - 1]
    season.series.sort(key=attrgetter("number"))
    serias = [{"number": number, "title": seria.number} for number, seria in enumerate(season.series, start=1)]

    return {
        "serias": serias,
        "is_admin": dialog_manager.middleware_data.get("is_admin", False)
    }


@tracker("Genres_getter: show genres menu")
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


@tracker("Account_getter: open account menu")
@inject
async def account_getter(
        dialog_manager: DialogManager,
        user_repository: UserRepository = Provide[Container.user_repository],
        **_kwargs
):
    text = []

    user = dialog_manager.middleware_data.get("user")
    is_admin = dialog_manager.middleware_data.get("is_admin")
    if is_admin:
        text.append("Статус: Администратор")

    for chat_id in settings.telegram.chats_id:
        user_sub_to_group = await is_user_subscribed(dialog_manager.event.bot, user.id, chat_id)
        text.append(f"Подписка на группу {chat_id}: {'✔' if user_sub_to_group else '❌'}")
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
        "text": "\n".join(text),
        "is_admin": is_admin,
        "sub_system_enable": not settings.disable_sub_system
    }


@tracker("Subscribe_getter: show menu")
@inject
async def subscribes_getter(
        dialog_manager: DialogManager,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
        **_kwargs
):
    subscribes = await subscribe_repository.all()
    subscribes.sort(key=attrgetter("days"), reverse=True)
    return {
        "subscribes": subscribes
    }


@tracker("Movie_getter: show poster window")
@inject
async def movie_poster_getter(
        dialog_manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service],
        **_kwargs
):
    movie_id = dialog_manager.dialog_data["movie_id"]
    movie = await movie_service.get(movie_id)

    message_text = f"<b>{movie.type.verbose}</b>: {movie.name}\n\n<b>Описание</b>:\n{movie.full_description}"

    return {
        "description": f"{message_text[:1021]}..." if len(message_text) >= 1024 else message_text,
        "photo": str(movie.poster)
    }


@tracker("Account_getter: show admin menu")
async def admin_manager_getter(
        dialog_manager: DialogManager,
        **_kwargs
):
    checkbox_sub_system = dialog_manager.find("admin_sub_system")
    await checkbox_sub_system.set_checked(not settings.disable_sub_system)
    return {}


@tracker("Admin_getter: show edit sub menu")
@inject
async def admin_edit_sub_getter(
        dialog_manager: DialogManager,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
        **_kwargs
):
    logger.debug(f"{dialog_manager.dialog_data=}")
    text_input = dialog_manager.find("subscribe_field_edit")
    edit_field = dialog_manager.dialog_data.get("subscribe_field_edit", None)
    edit_mode = dialog_manager.dialog_data.get("edit_mode", False)
    edit = dialog_manager.dialog_data.get("edit", False)
    if text_input is not None and edit_field is not None:
        dialog_manager.dialog_data[edit_field] = text_input.get_value()
        logger.debug(f"{text_input.get_value()=}")

        del dialog_manager.dialog_data["subscribe_field_edit"]

    logger.debug(f"{dialog_manager.dialog_data=}")
    if edit is False:
        if edit_mode is False:
            dialog_manager.dialog_data['name'] = dialog_manager.find("sub_name").get_value()
            dialog_manager.dialog_data['amount'] = dialog_manager.find("sub_amount").get_value()
            dialog_manager.dialog_data['days'] = dialog_manager.find("sub_days").get_value()
            dialog_manager.dialog_data['edit_mode'] = True

        return {
            "fields": [
                schemes.EditField("Название", "name"),
                schemes.EditField("Цена", "amount"),
                schemes.EditField("Длительность", "days")
            ],
            "new_text": "\n".join([
                "\n<b>Обновленные данные:</b>",
                f"Название: {dialog_manager.dialog_data.get('name', '-')}",
                f"Цена: {dialog_manager.dialog_data.get('amount', '-')} руб.",
                f"Длительность: {dialog_manager.dialog_data.get('days', '-')}"
            ]),
            "edit": edit,
        }

    subscribe_id = dialog_manager.dialog_data.get("subscribe_id", None)
    if subscribe_id is None:
        await dialog_manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)
        return

    subscribe = await subscribe_repository.get(subscribe_id)
    if subscribe is None:
        await dialog_manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)
        return

    return {
        "fields": [
            schemes.EditField("Название", "name"),
            schemes.EditField("Цена", "amount"),
            schemes.EditField("Длительность", "days")
        ],
        "text": "\n".join([
            "<b>Текущие данные:</b>",
            f"Название: {subscribe.name}",
            f"Цена: {subscribe.amount} руб.",
            f"Длительность: {subscribe.days}"
        ]),
        "new_text": "\n".join([
            "\n<b>Обновленные данные:</b>",
            f"Название: {dialog_manager.dialog_data.get('name', '-')}",
            f"Цена: {dialog_manager.dialog_data.get('amount', '-')} руб.",
            f"Длительность: {dialog_manager.dialog_data.get('days', '-')}"
        ]),
        "edit": edit
    }
