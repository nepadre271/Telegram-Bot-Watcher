from operator import itemgetter

from aiogram.enums import ContentType, ParseMode
from aiogram_dialog import (
    Dialog,
    Window
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    NextPage, PrevPage, Row,
    ScrollingGroup, Select, SwitchTo, Button, Back
)
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from magic_filter import F

from bot.dialogs import selected, const, getters, keyboards
from bot.states import DialogSG, DialogSelectGenres, DialogAccount, DialogAdmin

video_select_dialog = Dialog(
    Window(
        Const("Выберите фильм/сериал"),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                id="movies",
                items="movies",
                item_id_getter=itemgetter("id"),
                on_click=selected.on_movie_select
            ),
            width=1,
            height=const.MOVIES_LIMIT,
            hide_pager=True,
            id="scroll_movies",
        ),
        Row(
            PrevPage(scroll="scroll_movies", id="__m_pager_prev__", when=keyboards.hide_back_button(True)),
            NextPage(scroll="scroll_movies", id="__m_pager_next__", when=keyboards.hide_next_button(True)),
        ),
        getter=getters.movies_getter,
        state=DialogSG.SELECT_MOVIE,
    ),
    Window(
        StaticMedia(url=Format("{photo}"), type=ContentType.PHOTO),
        Format("{description}"),
        Button(Const("Начать просмотр"), id="show_poster_btn", on_click=selected.on_watch_btn_selected),
        getter=getters.movie_poster_getter,
        state=DialogSG.SHOW_POSTER,
        parse_mode="HTML"
    ),
    Window(
        Const("Выберите Сезон"),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                id="seasons",
                items="seasons",
                item_id_getter=itemgetter("number"),
                on_click=selected.on_season_select
            ),
            width=1,
            height=const.SEASONS_LIMIT,
            hide_pager=True,
            id="scroll_seasons",
        ),
        Row(
            PrevPage(scroll="scroll_seasons", id="__sea_pager_prev__", when=keyboards.hide_back_button(False)),
            NextPage(scroll="scroll_seasons", id="__sea_pager_next__", when=keyboards.hide_next_button(False)),
        ),
        SwitchTo(
            Const("К выбору фильмов/сериалов"),
            state=DialogSG.SELECT_MOVIE,
            id="SeasonsBack"
        ),
        getter=getters.seasons_getter,
        state=DialogSG.SELECT_SEASON,
    ),
    Window(
        Const("Выберите Серию"),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                id="serias",
                items="serias",
                item_id_getter=itemgetter("number"),
                on_click=selected.on_seria_select
            ),
            width=2,
            height=const.SERIAS_LIMIT // 2,
            hide_pager=True,
            id="scroll_serias",
        ),
        Row(
            PrevPage(scroll="scroll_serias", id="__ser_pager_prev__", when=keyboards.hide_back_button(False)),
            NextPage(scroll="scroll_serias", id="__ser_pager_next__", when=keyboards.hide_next_button(False)),
        ),
        Button(
            Const("Загрузить весь сезон"),
            on_click=selected.on_season_upload_clicked,
            id="SeasonUpload",
            when=F["is_admin"]
        ),
        SwitchTo(
            Const("К выбору сезонов"),
            state=DialogSG.SELECT_SEASON,
            id="SeriasBack"
        ),
        getter=getters.serias_getter,
        state=DialogSG.SELECT_SERIA,
    ),
)

genres_select_dialog = Dialog(
    Window(
        Const("Выберите жанры"),
        keyboards.get_genres_keyboard(),
        keyboards.get_genres_keyboard_scroller(),
        Button(
            Const("Поиск"),
            id="genres_search",
            on_click=selected.on_genres_search_clicked
        ),
        state=DialogSelectGenres.SELECT_GENRE,
        getter=getters.genres_getter
    ),
)

account_dialog = Dialog(
    Window(
        Format("{text}"),
        keyboards.get_account_main_keyboard(),
        state=DialogAccount.MAIN,
        getter=getters.account_getter
    ),
    Window(
        Const("Выберите подписку"),
        keyboards.get_subscribes_keyboard(),
        keyboards.get_subscribes_keyboard_scroller(),
        Back(Const("К аккаунту")),
        state=DialogAccount.SELECT_SUBSCRIBE,
        getter=getters.subscribes_getter
    )
)

admin_dialog = Dialog(
    Window(
        Const("Управление"),
        keyboards.get_admin_main_keyboard(),
        state=DialogAdmin.MAIN,
        getter=getters.admin_manager_getter
    ),
    Window(
        Const("Управление подписками"),
        keyboards.get_subscribes_keyboard(on_click=selected.on_sub_edit_selected),
        keyboards.get_subscribes_keyboard_scroller(),
        keyboards.get_switch_to_admin_sub_add(),
        keyboards.get_keyboard_to_admin_main(),
        state=DialogAdmin.SELECT_SUBSCRIBE,
        getter=getters.subscribes_getter
    ),
    Window(
        Const("Введите название подписки"),
        TextInput(id="sub_name", on_success=selected.on_text_input),
        keyboards.get_admin_add_sub_cancel(),
        state=DialogAdmin.SUBSCRIBE_INPUT_NAME_FIELD,
    ),
    Window(
        Const("Введите цену"),
        TextInput(id="sub_amount", on_success=selected.on_text_input),
        keyboards.get_admin_add_sub_cancel(),
        state=DialogAdmin.SUBSCRIBE_INPUT_AMOUNT_FIELD,
    ),
    Window(
        Const("Введите количество дней"),
        TextInput(id="sub_days", on_success=selected.on_text_input),
        keyboards.get_admin_add_sub_cancel(),
        state=DialogAdmin.SUBSCRIBE_INPUT_DAYS_FIELD,
    ),
    Window(
        Const("Изменение подписки\n"),
        Format("{text}", when=F["edit"]),
        Format("{new_text}"),
        keyboards.get_admin_sub_edit(),
        keyboards.get_keyboard_to_admin_main(),
        state=DialogAdmin.EDIT_SUBSCRIBE,
        getter=getters.admin_edit_sub_getter,
        parse_mode=ParseMode.HTML
    ),
    Window(
        Const("Введите новое значение"),
        TextInput(id="subscribe_field_edit", on_success=selected.on_text_input),
        SwitchTo(text=Const("Отмена"), state=DialogAdmin.EDIT_SUBSCRIBE, id="sub_edit_back"),
        state=DialogAdmin.SUBSCRIBE_EDIT_FIELD,
    ),
)
