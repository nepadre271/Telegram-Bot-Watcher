from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


def create_movie_buttons(results, current_index, total_results) -> InlineKeyboardMarkup:
    navigation_buttons = []
    kb = InlineKeyboardBuilder()

    for movie in results:
        button_text = f"{movie['name']} ({movie['year']})"
        callback_data = f"movie:{movie['id']}"
        kb.row(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    if current_index >= 10:
        navigation_buttons.append(InlineKeyboardButton(text="« Назад", callback_data="pages:prev_page"))

    if current_index + 10 < total_results:
        navigation_buttons.append(InlineKeyboardButton(text="Далее »", callback_data="pages:next_page"))

    if navigation_buttons:
        kb.row(*navigation_buttons)

    return kb.as_markup()
