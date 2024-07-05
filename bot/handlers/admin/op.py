from dependency_injector.wiring import Provide, inject
from aiogram import Router, F, types, filters
from aiogram.enums import ParseMode

from bot.utils import only_admin_handler, tracker
from core.repositories import UserRepository
from bot.containers import Container
from bot.database.models import User

router = Router()


async def _op_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repository: UserRepository
) -> User | None:
    error_message = "\n".join([
        "Ошибка: передайте @username или id пользователя.",
        "Пользователь может получить свой id введя команду <code>/id</code>"
    ])
    if command.args is None:
        await message.answer(error_message, parse_mode=ParseMode.HTML)
        return

    user = None
    user_id = command.args.split(" ")[0]
    if user_id.isdigit():
        user = await user_repository.get(int(user_id))
    elif "@" in user_id:
        user = await user_repository.get_by_username(user_id[1:])

    if user is None:
        await message.answer("Ошибка: Пользователь не найден в Базе данных")
        await message.answer(error_message, parse_mode=ParseMode.HTML)

    return user


@router.message(F.text, filters.Command("op"))
@only_admin_handler
@tracker("Admin: op user")
@inject
async def op_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repository: UserRepository = Provide[Container.user_repository],
        **kwargs
):
    user = await _op_handler(message, command, user_repository)
    if user is None:
        return
    await user_repository.change_admin_status(user, True)
    await message.answer(f"Пользователь @{user.username} [{user.id}] получил статус администратора")


@router.message(F.text, filters.Command("deop"))
@only_admin_handler
@tracker("Admin: deop user")
@inject
async def deop_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repository: UserRepository = Provide[Container.user_repository],
        **kwargs
):
    user = await _op_handler(message, command, user_repository)
    if user is None:
        return
    await user_repository.change_admin_status(user, False)
    await message.answer(f"Пользователь @{user.username} [{user.id}] перестал быть администратором")
