from typing import Callable
import operator

from aiogram_dialog.widgets.kbd import Multiselect, Keyboard, ScrollingGroup, NextPage, PrevPage, Row, Button, Select, \
    Next, Checkbox, Column, Start, SwitchTo
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog import DialogManager
from magic_filter import F

from bot.handlers.user.subscribe import process_buy_command
from bot.dialogs import selected
from bot import states


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


def get_account_main_keyboard() -> Keyboard:
    return Column(
        Row(
            Button(Const("Реф. ссылка"), id="acc_ref", on_click=selected.on_ref_button_clicked),
            Next(Const("Купить подписку"), id="acc_sub", when=F["sub_system_enable"])
        ),
        Start(
            Const("Управление"),
            state=states.DialogAdmin.MAIN,
            when=F["is_admin"],
            id="admin_manager"
        )
    )


def get_subscribes_keyboard(on_click: Callable = process_buy_command) -> Keyboard:
    return ScrollingGroup(
        Select(
            Format("{item.name} ({item.amount} руб.)"),
            id="subscribe",
            item_id_getter=operator.attrgetter("id"),
            items="subscribes",
            on_click=on_click
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


def get_keyboard_to_admin_main() -> Keyboard:
    return SwitchTo(
        text=Const("К меню управления"),
        state=states.DialogAdmin.MAIN,
        id="back_to_admin_menu",
        on_click=selected.on_clicked_clear_data
    )


def get_admin_main_keyboard() -> Keyboard:
    return Column(
        Checkbox(
            checked_text=Const("✔ Система подписки вкл."),
            unchecked_text=Const("❌ Система подписки выкл."),
            id="admin_sub_system",
            on_click=selected.on_sub_system_checkbox_click
        ),
        SwitchTo(
            text=Const("Редактирование тарифов"),
            id="admin_edit_subs",
            state=states.DialogAdmin.SELECT_SUBSCRIBE
        ),
        Start(Const("К аккаунту"), state=states.DialogAccount.MAIN, id="admin_back_acc")
    )


def get_admin_sub_edit() -> Keyboard:
    return Column(
        Select(
            text=Format("{item.label}"),
            id="sub_edit",
            item_id_getter=operator.attrgetter("name"),
            items="fields",
            on_click=selected.on_sub_edit_field_selected
        ),
        Button(
            text=Const("✔ Сохранить ✔"),
            on_click=selected.on_sub_save_clicked,
            id="sub_save"
        ),
        Button(
            text=Const("🔥 Удалить 🔥"),
            on_click=selected.on_sub_delete_clicked,
            id="sub_delete", when=F["edit"]
        )
    )


def get_admin_add_sub_cancel() -> Keyboard:
    return Column(
        SwitchTo(text=Const("Отмена"), state=states.DialogAdmin.SELECT_SUBSCRIBE, id="sub_add_cancel")
    )


def get_switch_to_admin_sub_add() -> Keyboard:
    return SwitchTo(
        text=Const("Добавить подписку"),
        state=states.DialogAdmin.SUBSCRIBE_INPUT_NAME_FIELD,
        id="to_add_sub",
        on_click=selected.on_clicked_clear_data
    )
