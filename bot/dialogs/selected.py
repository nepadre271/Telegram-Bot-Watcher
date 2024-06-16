from typing import Any

from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from dependency_injector.wiring import Provide, inject
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox
from aiogram_dialog import DialogManager, ChatEvent
from loguru import logger

from core.repositories import UserRepository, SubscribeRepository
from bot.handlers.user.callback import process_movie_callback
from bot.schemes import UploadMovieCallbackFactory
from core.services import MovieService
from bot.containers import Container
from bot.settings import settings
from bot import states


@logger.catch()
@inject
async def on_movie_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str,
        movie_service: MovieService = Provide[Container.movie_service]
):
    logger.debug(f"[{callback.message.chat.id}] Select {item_id}")
    if not item_id:
        return

    movie = await movie_service.get(int(item_id))
    if movie is None:
        message_text = "Недоступен для просмотра/загрузки ❌"
        await callback.answer(message_text)
        return

    manager.dialog_data["movie_id"] = movie.id
    await manager.next()


@logger.catch()
@inject
async def on_watch_btn_selected(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        movie_service: MovieService = Provide[Container.movie_service]
):
    movie = await movie_service.get(manager.dialog_data["movie_id"])

    if movie.type != "film":
        await manager.next()
        return

    callback_data = UploadMovieCallbackFactory(
        id=movie.id
    )
    await process_movie_callback(
        callback,
        callback_data,
        bot=callback.bot
    )


async def on_season_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    logger.debug(f"[{callback.message.chat.id}] Select {manager.dialog_data['movie_id']}:{item_id}")
    if not item_id:
        return

    manager.dialog_data["season_number"] = int(item_id)
    await manager.next()


@logger.catch()
@inject
async def on_seria_select(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    logger.debug(
        f"[{callback.message.chat.id}] Select {manager.dialog_data['movie_id']}:{manager.dialog_data['season_number']}:{item_id}")
    if not item_id:
        return

    manager.dialog_data["seria_number"] = int(item_id)
    callback_data = UploadMovieCallbackFactory(
        id=manager.dialog_data["movie_id"],
        season=manager.dialog_data["season_number"],
        seria=manager.dialog_data["seria_number"]
    )
    await process_movie_callback(query=callback, callback_data=callback_data, bot=callback.bot)


async def on_genres_search_clicked(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager
):
    genres_list = manager.find('multi_genres')
    genres = genres_list.get_checked()
    logger.debug(f"User[{callback.message.chat.id}] select genres: {genres}")

    if len(genres) < 1:
        await callback.answer("Выберите один или несколько жанров")
        return

    await manager.start(
        states.DialogSG.SELECT_MOVIE,
        data={
            "query": {
                "genres.name": genres,
                "sortField": ["rating.kp"],
                "sortType": "-1"
            }
        }
    )


@inject
async def on_ref_button_clicked(
        callback: CallbackQuery, button: Button, manager: DialogManager,
        user_repository: UserRepository = Provide[Container.user_repository]
):
    user_id = callback.message.chat.id
    user = await user_repository.get(user_id)
    link = await create_start_link(callback.message.bot, payload=f"ref:{user.ref}", encode=True)
    await callback.message.answer(f"Ваша реф. ссылка <code>{link}</code>", parse_mode=ParseMode.HTML)


async def on_sub_system_checkbox_click(event: ChatEvent, checkbox: ManagedCheckbox,
                        manager: DialogManager):
    system_status = not settings.disable_sub_system
    settings.disable_sub_system = system_status

    if system_status:
        await event.message.answer("System: система подписок отключена ❌")
    else:
        await event.message.answer("System: система подписок включена ✔")


async def on_sub_edit_selected(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    manager.dialog_data["subscribe_id"] = int(item_id)
    manager.dialog_data["edit"] = True
    await manager.switch_to(state=states.DialogAdmin.EDIT_SUBSCRIBE)


async def on_sub_edit_field_selected(
        callback: CallbackQuery, widget: Any,
        manager: DialogManager, item_id: str
):
    # fields = {
    #     "name": states.DialogAdmin.SUBSCRIBE_INPUT_NAME_FIELD,
    #     "amount": states.DialogAdmin.SUBSCRIBE_INPUT_AMOUNT_FIELD,
    #     "days": states.DialogAdmin.SUBSCRIBE_INPUT_DAYS_FIELD
    # }
    manager.dialog_data["subscribe_field_edit"] = item_id
    await manager.switch_to(
        # state=states.DialogAdmin.SUBSCRIBE_EDIT_FIELD if manager.dialog_data.get("edit", False) else fields[item_id]
        state=states.DialogAdmin.SUBSCRIBE_EDIT_FIELD
    )


async def on_text_input(event, widget, dialog_manager: DialogManager, *_):
    if dialog_manager.dialog_data.get("edit") or dialog_manager.dialog_data.get("edit_mode"):
        await dialog_manager.switch_to(state=states.DialogAdmin.EDIT_SUBSCRIBE)
    else:
        await dialog_manager.next()


@inject
async def on_sub_save_clicked(
        callback: CallbackQuery, button: Button, manager: DialogManager,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository]
):
    data = manager.dialog_data

    subscribe_id = data.get("subscribe_id")
    subscribe = None

    new_data = dict()
    if subscribe_id:
        subscribe = await subscribe_repository.get(subscribe_id)
        new_data.update({
            "name": subscribe.name,
            "amount": subscribe.amount,
            "days": subscribe.days
        })

    if name := data.get("name", None):
        new_data["name"] = name

    if amount := data.get("amount", None):
        try:
            new_data["amount"] = int(amount)
        except ValueError:
            await callback.message.answer(f"Ошибка поле: Цена не должно содержать символов")
            return
        if new_data["amount"] < 60:
            await callback.message.answer(f"Ошибка поле: Цена не может быть ниже 60 рублей")
            return

    if days := data.get("days", None):
        try:
            new_data["days"] = int(days)
        except ValueError:
            await callback.message.answer(f"Ошибка поле: Длительность не должно содержать символов")
            return

    await subscribe_repository.create(**new_data)
    if subscribe:
        await subscribe_repository.toggle_visibility(subscribe)

    manager.dialog_data.clear()
    await manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)


@inject
async def on_sub_delete_clicked(
        callback: CallbackQuery, button: Button, manager: DialogManager,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository]
):
    subscribe_id = manager.dialog_data.get("subscribe_id", None)
    if subscribe_id is None:
        await callback.answer(text="Отсутствует subscribe_id")
        await manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)
        return

    subscribe = await subscribe_repository.get(subscribe_id)
    if subscribe is None:
        await callback.answer(text=f"Подписка с id:{subscribe_id} не существует")
        await manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)
        return

    await subscribe_repository.toggle_visibility(subscribe)
    await callback.answer(text=f"Подписка с id:{subscribe_id} удалена")
    manager.dialog_data.clear()
    await manager.switch_to(state=states.DialogAdmin.SELECT_SUBSCRIBE)


async def on_clicked_clear_data(
        callback: CallbackQuery, button: Button, manager: DialogManager,
):
    manager.dialog_data.clear()
