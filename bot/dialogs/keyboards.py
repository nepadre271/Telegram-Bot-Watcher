from aiogram_dialog import (
    DialogManager,
)
from aiogram_dialog.widgets.common import Whenable


def hide_back_button(data: dict, widget: Whenable, manager: DialogManager):
    data = data["data"]["dialog_data"]
    try:
        return data["page"] > 1
    except (KeyError, TypeError):
        return True


def hide_next_button(data: dict, widget: Whenable, manager: DialogManager):
    data = data["data"]["dialog_data"]
    try:
        return data["page"] <= data["total_pages"]
    except (KeyError, TypeError):
        return True
