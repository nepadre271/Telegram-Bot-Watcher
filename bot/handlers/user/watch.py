from aiogram import Router, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dependency_injector.wiring import inject, Provide
from loguru import logger

from bot.schemes.movie import SelectMovieCallbackFactory, UploadMovieCallbackFactory
from core.services.movie import MovieService
from bot.containers import Container

router = Router()


@router.callback_query(SelectMovieCallbackFactory.filter())
@logger.catch()
@inject
async def select_movie(
        query: types.CallbackQuery,
        callback_data: SelectMovieCallbackFactory,
        movie_service: MovieService = Provide[Container.movie_service]
):
    movie = await movie_service.get(callback_data.id)

    if movie is None:
        logger.error(f"Данные о фильме отсутствуют ID:{callback_data.id}")
        await query.message.answer("Извините, информация о фильме не найдена.")
        return

    message_text = f"<b>{movie.type.verbose}</b>: {movie.name}\n\n<b>Описание</b>:\n{movie.full_description}"

    logger.info(
        f"Обработчик process_movie_callback отправил сообщение с информацией о '{movie.name}' (id:{movie.id})")
    image = types.URLInputFile(str(movie.poster))
    await query.message.answer_photo(
        photo=image,
        caption=message_text,
        parse_mode="html",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="Начать просмотр",
                callback_data=UploadMovieCallbackFactory(
                    id=movie.id
                ).pack()
            )
        ]])
    )
