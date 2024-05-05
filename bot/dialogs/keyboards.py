from aiogram_dialog import (
    DialogManager,
)
from aiogram_dialog.widgets.common import Whenable


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
