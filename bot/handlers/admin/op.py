from aiogram import Router, F, types, filters
from aiogram.enums import ParseMode

from core.repositories import UserRepository
from bot.utils import only_admin_handler
from bot.database.models import User

router = Router()


async def _op_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repository: UserRepository
) -> User | None:
    error_message = "\n".join([
        "Ошибка: передайте id пользователя.",
        "Пользователь может получить свой id введя команду <code>/id</code>"
    ])
    if command.args is None:
        await message.answer(error_message, parse_mode=ParseMode.HTML)
        return

    user_id = command.args.split(" ")[0]
    if user_id.isdigit() is False:
        await message.answer(error_message)
        return

    user = await user_repository.get(int(user_id))
    return user


@router.message(F.text, filters.Command("op"))
@only_admin_handler
async def op_handler(
        message: types.Message,
        command: filters.CommandObject,
        **kwargs
):
    user_repository: UserRepository = kwargs["user_repository"]
    user = await _op_handler(message, command, user_repository)
    if user is None:
        return
    await user_repository.change_admin_status(user, True)
    await message.answer(f"Пользователь[{user.id}] получил статус администратора")


@router.message(F.text, filters.Command("deop"))
@only_admin_handler
async def deop_handler(
        message: types.Message,
        command: filters.CommandObject,
        **kwargs
):
    user_repository: UserRepository = kwargs["user_repository"]
    user = await _op_handler(message, command, user_repository)
    if user is None:
        return
    await user_repository.change_admin_status(user, False)
    await message.answer(f"Пользователь[{user.id}] перестал быть администратором")
