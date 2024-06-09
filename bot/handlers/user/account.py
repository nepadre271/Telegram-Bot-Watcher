from aiogram_dialog import StartMode, DialogManager
from aiogram import Router, F, types

from bot.states import DialogAccount

router = Router()


@router.message(F.text.lower() == 'аккаунт')
async def account_handler(
        message: types.Message,
        dialog_manager: DialogManager
):
    await dialog_manager.start(
        DialogAccount.MAIN, mode=StartMode.RESET_STACK
    )


