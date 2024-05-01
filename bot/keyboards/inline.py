from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.schemes import PageCallbackFactory, SelectMovieCallbackFactory
from core.schemes.movie.kinopoisk import SearchResponse
from bot.settings import settings


def unsub() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Подписаться на канал", url=settings.chat_url
    )
    kb.button(
        text="Начать просмотр", callback_data="get_started"
    )
    kb.adjust(1)
    return kb.as_markup()


def create_movie_buttons(data: SearchResponse, query_hash: str) -> InlineKeyboardMarkup:
    navigation_buttons = []
    kb = InlineKeyboardBuilder()

    for movie in data.movies:
        button_text = f"{movie.name} ({movie.year})"
        callback_data = SelectMovieCallbackFactory(id=movie.id).pack()
        kb.row(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    current_page = data.page
    if current_page > 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="« Назад", 
                callback_data=PageCallbackFactory(
                    number=current_page - 1, 
                    query_hash=query_hash
                ).pack()
            )
        )

    if current_page < data.pages:
        navigation_buttons.append(
            InlineKeyboardButton(
                text="Далее »", 
                callback_data=PageCallbackFactory(
                    number=current_page + 1, 
                    query_hash=query_hash
                ).pack()
            )
        )

    if navigation_buttons:
        kb.row(*navigation_buttons)

    return kb.as_markup()
