from operator import itemgetter

from aiogram_dialog import (
    Dialog,
    Window
)
from aiogram_dialog.widgets.kbd import (
    NextPage, PrevPage, Row, ScrollingGroup,
    Select, Back
)
from aiogram_dialog.widgets.text import Const, Format
from bot.dialogs.states import DialogSG
from bot.dialogs import selected, const, getters, keyboards


dialog = Dialog(
    Window(
        Const("Выберите фильм"),
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
            PrevPage(scroll="scroll_movies", id="__m_pager_prev__", when=keyboards.hide_back_button),
            NextPage(scroll="scroll_movies", id="__m_pager_next__", when=keyboards.hide_next_button),
        ),
        getter=getters.movies_getter,
        state=DialogSG.SELECT_MOVIE,
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
            PrevPage(scroll="scroll_seasons", id="__sea_pager_prev__", when=keyboards.hide_back_button),
            NextPage(scroll="scroll_seasons", id="__sea_pager_next__", when=keyboards.hide_next_button),
        ),
        Back(
            Const("К выбору фильмов/сериалов")
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
            PrevPage(scroll="scroll_serias", id="__ser_pager_prev__", when=keyboards.hide_back_button),
            NextPage(scroll="scroll_serias", id="__ser_pager_next__", when=keyboards.hide_next_button),
        ),
        Back(
            Const("К выбору сезонов")
        ),
        getter=getters.serias_getter,
        state=DialogSG.SELECT_SERIA,
    ),
)
