
from typing import Any

from aiogram import types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject
from loguru import logger

from bot.dialogs.states import DialogSG
from bot.schemes import UploadMovieCallbackFactory
from core.schemes.movie.kinoclub import MovieType
from core.services import MovieService, UploaderService
from core.schemes.uploader import UploadMovieRequest

from bot.containers import Container


@logger.catch()
@inject
async def on_movie_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str,
        movie_service: MovieService = Provide[Container.movie_service]
):
    logger.debug(item_id)
    if not item_id:
        return

    movie = await movie_service.get(int(item_id))
    if movie is None:
        message_text = "Недоступен для просмотра/загрузки ❌"
        await callback.answer(message_text)
        return
    
    if movie.type != "film":
        manager.dialog_data["movie_id"] = movie.id
        await manager.next()
        return

    await callback.answer(f"Выбран фильм: {movie.name}")
    message_text = f"<b>{movie.type.verbose}</b>: {movie.name}\n\n<b>Описание</b>:\n{movie.full_description}"
    
    logger.info(
        f"Обработчик process_movie_callback отправил сообщение с информацией о '{movie.name}' (id:{movie.id})")
    image = types.URLInputFile(str(movie.poster))

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Начать просмотр",
            callback_data=UploadMovieCallbackFactory(
                id=movie.id
            ).pack()
        )
    ]])

    await callback.message.answer_photo(
        photo=image,
        caption=message_text,
        parse_mode="html",
        reply_markup=keyboard
    )


async def on_season_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    logger.debug(item_id)
    if not item_id:
        return

    manager.dialog_data["season_number"] = int(item_id)
    await manager.next()


@logger.catch()
@inject
async def on_seria_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str,
        uploader_service: UploaderService = Provide[Container.uploader_service]
):
    logger.debug(item_id)
    if not item_id:
        return

    manager.dialog_data["seria_number"] = int(item_id)
    logger.debug(manager.dialog_data)
    request = UploadMovieRequest(
        movie_id=manager.dialog_data["movie_id"],
        season=manager.dialog_data["season_number"],
        seria=manager.dialog_data["seria_number"],
        type=MovieType.SERIAL,
        user_id=callback.message.chat.id
    )
    await uploader_service.upload_movie(request)
