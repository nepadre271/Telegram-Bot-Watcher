from operator import attrgetter

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.schemes.uploader import UploadMovieRequest
from bot.schemes import UploadMovieCallbackFactory
from core.schemes.movie.kinoclub import Movie
from bot.settings import settings


def create_sub_block(callback_data: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for chat_id in settings.telegram.chats_id:
        kb.button(
            text=f"Подписаться на канал {chat_id}", url=f"https://t.me/{chat_id[1:]}"
        )
    kb.button(
        text="Начать просмотр", callback_data=callback_data
    )
    kb.adjust(1)
    return kb.as_markup()


def create_movie_nav(movie: Movie, data: UploadMovieRequest) -> InlineKeyboardMarkup | None:
    kb = InlineKeyboardBuilder()
    if movie.type == "film":
        return None

    current_seria = data.seria
    current_season = data.season

    series = movie.seasons[current_season-1].series
    series.sort(key=attrgetter("number"))
    series_count = len(series)
    seasons_count = len(movie.seasons)

    series_nav = []
    if current_seria > 1:
        series_nav.append(
            InlineKeyboardButton(
                text=f"« Серия {series[current_seria - 2].number}",
                callback_data=UploadMovieCallbackFactory(
                    id=movie.id, season=current_season, seria=current_seria - 1
                ).pack()
            )
        )
    if series_count > current_seria:
        series_nav.append(
            InlineKeyboardButton(
                text=f"Серия {series[current_seria].number} »",
                callback_data=UploadMovieCallbackFactory(
                    id=movie.id, season=current_season, seria=current_seria + 1
                ).pack()
            )
        )
    kb.row(*series_nav)

    if current_season > 1 and current_seria == 1:
        kb.row(
            InlineKeyboardButton(
                text="Следующий сезон",
                callback_data=UploadMovieCallbackFactory(
                    id=movie.id, season=current_season - 1, seria=1
                ).pack()
            )
        )

    if seasons_count > current_season and current_seria == series_count:
        kb.row(
            InlineKeyboardButton(
                text="Предыдущий сезон",
                callback_data=UploadMovieCallbackFactory(
                    id=movie.id, season=current_season + 1, seria=1
                ).pack()
            )
        )

    return kb.as_markup()
