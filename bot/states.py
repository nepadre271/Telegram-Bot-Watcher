from aiogram.fsm.state import StatesGroup, State


class DialogSG(StatesGroup):
    SELECT_MOVIE = State()
    SELECT_SEASON = State()
    SELECT_SERIA = State()


class DialogSelectGenres(StatesGroup):
    SELECT_GENRE = State()


class DialogAccount(StatesGroup):
    MAIN = State()
    SELECT_SUBSCRIBE = State()
