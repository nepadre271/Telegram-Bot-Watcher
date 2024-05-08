from operator import itemgetter

from aiogram_dialog import (
    Dialog,
    Window
)
from aiogram_dialog.widgets.kbd import (
    NextPage, PrevPage, Row,
    ScrollingGroup, Select, SwitchTo, Button
)
from aiogram_dialog.widgets.text import Const, Format
from bot.dialogs import selected, const, getters, keyboards
from bot.states import DialogSG, DialogSelectGenres

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
