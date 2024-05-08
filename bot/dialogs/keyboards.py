import operator

from aiogram_dialog.widgets.kbd import Multiselect, Keyboard, ScrollingGroup, NextPage, PrevPage, Row
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.text import Format
from aiogram_dialog import DialogManager


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
