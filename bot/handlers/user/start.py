import logging

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from bot.utils import is_user_subscribed
from bot.keyboards.reply import main_menu
from bot.keyboards.inline import unsub
from bot.settings import settings

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot):
    logger.info("Обработчик cmd_start вызван")
    user_id = message.from_user.id
    channel_id = settings.chat_id
    if await is_user_subscribed(bot, user_id, channel_id):
        logger.info("Пользователь подписан на канал")
        text = f"<b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n" + \
               "📺 Вы находитесь в лучшем боте для просмотра фильмов и сериалов прямо в Telegram!\n\n" + \
               "Смотрите сериалы на телефоне, планшете и компьютере." + \
               "Подписывайтесь на уведомления о новых сериях. Сортируйте сериалы по названию, жанрам и интересам." + \
               "Скачивайте сериалы себе на устройство и смотрите без интернета.\n\n" + \
               "<i>Используя бота, вы подтверждаете, что будете соблюдать возрастные ограничения сериалов.</i>"

        markup = main_menu()

    else:
        logger.info("Пользователь не подписан на канал")
        text = f"<b>Добро пожаловать, {message.from_user.first_name}!</b>\n\n" + \
               "Чтобы приступить к просмотру сериалов в боте, необходимо подписаться на наш канал " + \
               "— для этого воспользуйтесь кнопками ниже!👇\n\n" + \
               "После подписки на канал вернитесь обратно и нажмите кнопку «Приступить к просмотру». \n\n" + \
               "<i>Бот работает для вас и без ограничений! Наслаждайтесь!</i>"

        markup = unsub()

    await message.answer(
        text,
        parse_mode="html",
        reply_markup=markup
    )
    logger.info("Обработчик cmd_start завершил работу")
