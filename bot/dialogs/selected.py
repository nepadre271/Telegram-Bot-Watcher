from typing import Any

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dependency_injector.wiring import Provide, inject
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import DialogManager
from aiogram import types
from loguru import logger

from bot.handlers.user.callback import process_movie_callback
from bot.schemes import UploadMovieCallbackFactory
from core.services import MovieService
from bot.containers import Container
from bot import states


@logger.catch()
@inject
async def on_movie_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str,
        movie_service: MovieService = Provide[Container.movie_service]
):
    logger.debug(f"[{callback.message.chat.id}] Select {item_id}")
    if not item_id:
        return

    movie = await movie_service.get(int(item_id))
    if movie is None:
        message_text = "Недоступен для просмотра/загрузки ❌"
        await callback.answer(message_text)
        return

    manager.dialog_data["movie_id"] = movie.id
    await manager.next()


@logger.catch()
@inject
async def on_watch_btn_selected(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service]
):
    movie = await movie_service.get(manager.dialog_data["movie_id"])

    if movie.type != "film":
        await manager.next()
        return

    callback_data = UploadMovieCallbackFactory(
        id=movie.id
    )
    await process_movie_callback(
        callback,
        callback_data,
        bot=callback.bot
    )


async def on_season_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    logger.debug(f"[{callback.message.chat.id}] Select {manager.dialog_data['movie_id']}:{item_id}")
    if not item_id:
        return

    manager.dialog_data["season_number"] = int(item_id)
    await manager.next()


@logger.catch()
@inject
async def on_seria_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    logger.debug(
        f"[{callback.message.chat.id}] Select {manager.dialog_data['movie_id']}:{manager.dialog_data['season_number']}:{item_id}")
    if not item_id:
        return

    manager.dialog_data["seria_number"] = int(item_id)
    callback_data = UploadMovieCallbackFactory(
        id=manager.dialog_data["movie_id"],
        season=manager.dialog_data["season_number"],
        seria=manager.dialog_data["seria_number"]
    )
    await process_movie_callback(query=callback, callback_data=callback_data, bot=callback.bot)


async def on_genres_search_clicked(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager
):
    genres_list = manager.find('multi_genres')
    genres = genres_list.get_checked()
    logger.debug(f"User[{callback.message.chat.id}] select genres: {genres}")

    if len(genres) < 1:
        await callback.answer("Выберите один или несколько жанров")
        return

    await manager.start(
        states.DialogSG.SELECT_MOVIE,
        data={
            "query": {
                "genres.name": genres,
                "sortField": ["rating.kp"],
                "sortType": "-1"
            }
        }
    )
