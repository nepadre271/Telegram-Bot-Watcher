from aiogram.fsm.state import StatesGroup, State


class DialogSG(StatesGroup):
    WAIT_NAME_INPUT = State()
    SELECT_MOVIE = State()
    SHOW_POSTER = State()
    SELECT_SEASON = State()
    SELECT_SERIA = State()


class DialogSelectGenres(StatesGroup):
    SELECT_GENRE = State()


class DialogAccount(StatesGroup):
    MAIN = State()
    SELECT_SUBSCRIBE = State()


class DialogAdmin(StatesGroup):
    MAIN = State()
    SELECT_SUBSCRIBE = State()
    EDIT_SUBSCRIBE = State()
    SUBSCRIBE_INPUT_NAME_FIELD = State()
    SUBSCRIBE_INPUT_AMOUNT_FIELD = State()
    SUBSCRIBE_INPUT_DAYS_FIELD = State()
    SUBSCRIBE_EDIT_FIELD = State()
