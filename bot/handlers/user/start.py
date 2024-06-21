from aiogram.filters import CommandStart, CommandObject, Command
from dependency_injector.wiring import Provide, inject
from aiogram.utils.deep_linking import decode_payload
from aiogram.types import Message
from aiogram import Router, Bot
from loguru import logger

from core.repositories.user import UserRepository
from bot.keyboards.reply import main_menu
from bot.containers import Container

router = Router()


async def _start_handler(message: Message):
    text = f"<b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n" + \
           "📺 Вы находитесь в лучшем боте для просмотра фильмов и сериалов прямо в Telegram!\n\n" + \
           "Смотрите сериалы на телефоне, планшете и компьютере." + \
           "Подписывайтесь на уведомления о новых сериях. Сортируйте сериалы по названию, жанрам и интересам." + \
           "Скачивайте сериалы себе на устройство и смотрите без интернета.\n\n" + \
           "<i>Используя бота, вы подтверждаете, что будете соблюдать возрастные ограничения сериалов.</i>"
    markup = main_menu()

    await message.answer(
        text,
        parse_mode="html",
        reply_markup=markup
    )


@router.message(CommandStart(deep_link=True), flags={"skip_user_middleware": True})
@inject
async def cmd_start_ref(
        message: Message, command: CommandObject, bot: Bot,
        user_repository: UserRepository = Provide[Container.user_repository]
):
    logger.info("Обработчик cmd_start вызван")
    logger.info(f"{command.args=}")
    await _start_handler(message)

    user_id = message.from_user.id
    user_exists = await user_repository.exists(user_id)
    payload = decode_payload(command.args)

    ref = None
    if payload.startswith("ref:"):
        ref = payload.replace("ref:", "")
        ref_owner = await user_repository.get_by_ref(ref)

        if ref_owner is not None and user_exists is False:
            await user_repository.update_views_count(ref_owner, 10)
            logger.info(f"Пользователь с id:{ref_owner.id} пригласил @{message.from_user.username} [id={user_id}]")
        else:
            ref = None

    if user_exists is False:
        await user_repository.create(user_id, ref)
    logger.info("Обработчик cmd_start завершил работу")


@router.message(Command("start"))
async def cmd_start_ref(
        message: Message
):
    logger.info("Обработчик cmd_start вызван")
    await _start_handler(message)
    logger.info("Обработчик cmd_start завершил работу")
