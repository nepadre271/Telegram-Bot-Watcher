from aiogram_dialog import StartMode, DialogManager
from aiogram import Router, F, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from bot.states import DialogAccount
from bot.utils import tracker

router = Router()


@router.message(F.text, filters.Command("id"), flags={"skip_user_middleware": True})
@tracker("Account: id command")
async def id_handler(message: types.Message, **kwargs):
    await message.answer(
        f"ID: <code>{message.chat.id}</code>",
        parse_mode=ParseMode.HTML
    )


@router.message(F.text.lower() == 'аккаунт')
@tracker("Account: open menu")
async def account_handler(
        message: types.Message,
        dialog_manager: DialogManager, state: FSMContext,
        **kwargs
):
    await state.set_state(state=None)
    await dialog_manager.start(
        DialogAccount.MAIN, mode=StartMode.RESET_STACK
    )


