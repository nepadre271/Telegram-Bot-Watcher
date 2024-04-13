from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="Поиск по названию🔎")
    )
    kb.row(
        KeyboardButton(text="По жанрам"),
        KeyboardButton(text="Рекомендации")
    )
    kb.row(
        KeyboardButton(text="Инструкция")
    )

    return kb.as_markup(resize_keyboard=True)
