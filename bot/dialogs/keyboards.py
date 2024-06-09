import operator

from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram_dialog.widgets.kbd import Multiselect, Keyboard, ScrollingGroup, NextPage, PrevPage, Row, Button, Select, Next
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject

from bot.handlers.user.subscribe import process_buy_command
from core.repositories import UserRepository
from bot.containers import Container


def hide_back_button(is_custom_pager: bool = False):
    def inner(data: dict, widget: Whenable, manager: DialogManager):
        nonlocal is_custom_pager
        if is_custom_pager is False:
            return data.get("current_page1", 1) > 1

        pager_data = data.get("data", {}).get("dialog_data", {})
        try:
            return pager_data["page"] > 1
        except (KeyError, TypeError):
            return True

    return inner


def hide_next_button(is_custom_pager: bool = False):
    def inner(data: dict, widget: Whenable, manager: DialogManager):
        nonlocal is_custom_pager
        if is_custom_pager is False:
            return data.get("current_page1", 1) < data.get("pages", 1)

        pager_data = data.get("data", {}).get("dialog_data", {})
        try:
            return pager_data["page"] <= pager_data["total_pages"]
        except (KeyError, TypeError):
            return True

    return inner


def get_next_page(dialog_manager: DialogManager, data: dict, prefix: str) -> int:
    pager_data = data.get("aiogd_original_callback_data", "")
    page = dialog_manager.dialog_data.get("page", 1)

    if f"{prefix}_pager_next" in pager_data:
        page = page + 1
    elif f"{prefix}_pager_prev" in pager_data:
        page = page - 1

    dialog_manager.dialog_data["page"] = page
    return page


def get_genres_keyboard() -> Keyboard:
    return ScrollingGroup(
        Multiselect(
            Format("✔ {item.name}"),
            Format("{item.name}"),
            id="multi_genres",
            item_id_getter=operator.attrgetter("name"),
            items="genres"
        ),
        id="scroll_genres",
        hide_pager=True,
        width=2,
        height=8
    )


def get_genres_keyboard_scroller() -> Keyboard:
    return Row(
        PrevPage(scroll="scroll_genres", id="__g_pager_prev__", when=hide_back_button()),
        NextPage(scroll="scroll_genres", id="__g_pager_next__", when=hide_next_button()),
    )


@inject
async def on_ref_button_clicked(
        callback: CallbackQuery, button: Button, manager: DialogManager,
        user_repository: UserRepository = Provide[Container.user_repository]
):
    user_id = callback.message.chat.id
    user = await user_repository.get(user_id)
    link = await create_start_link(callback.message.bot, payload=f"ref:{user.ref}", encode=True)
    await callback.message.answer(f"Ваша реф. ссылка {link}")


def get_account_main_keyboard() -> Keyboard:
    return Row(
        Button(Const("Реф. ссылка"), id="acc_ref", on_click=on_ref_button_clicked),
        Next(Const("Купить подписку"), id="acc_sub")
    )

def get_subscribes_keyboard() -> Keyboard:
    return ScrollingGroup(
        Select(
            Format("{item.name}"),
            id="subscribe",
            item_id_getter=operator.attrgetter("id"),
            items="subscribes",
            on_click=process_buy_command
        ),
        id="scroll_subscribes",
        hide_pager=True,
        width=1,
        height=10
    )


def get_subscribes_keyboard_scroller() -> Keyboard:
    return Row(
        PrevPage(scroll="scroll_subscribes", id="__s_pager_prev__", when=hide_back_button()),
        NextPage(scroll="scroll_subscribes", id="__s_pager_next__", when=hide_next_button()),
    )

