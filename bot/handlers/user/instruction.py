from aiogram.types import Message
from aiogram import Router, F
from loguru import logger

from bot.utils import tracker

router = Router()


@router.message(F.text.lower() == 'инструкция', flags={"skip_user_middleware": True})
@tracker("Instruction: show")
async def get_instruction(message: Message, **kwargs):
    logger.info("Обработчик get_instruction вызван")
    text = """
        <b>Как загрузить видео в телефон, планшет или компьютер для просмотра без интернета?</b>

        Чтобы загрузить видео в кэш приложения, просто нажмите слева-сверху на кнопку со стрелочкой, затем дождитесь загрузки. После этого вы сможете в любой момент вернуться в Telegram и начать просмотр, даже если у вас не будет интернета. Также вы можете сохранить любое загруженное видео в свою галерею или фотопоток.

        <b>Почему каждое видео имеет небольшой вес?</b>

        В нашем боте все серии имеют меньший размер, чем обычно. Это связано с тем, что большинство пользователей смотрят сериалы с мобильных устройств, а значит можно ужать качество видео и сэкономить на трафике и памяти устройства.

        <b>После просмотра нескольких серий закончилось место или перестало воспроизводиться видео, что делать?</b>

        Все видео сохраняются в кэш устройства, тем самым заполняя память. Но Telegram позволяет легко очистить кэш. Для этого нужно зайти в Настройки Telegram → Данные и память → Использование памяти → Очистить кэш.

        <b>Можно ли смотреть видео в боте и не платить за мобильный интернет?</b>

        Да, наш бот позволяет смотреть сериалы и при этом не платить за трафик. Такое возможно у некоторых операторов, которые предоставляют услугу «Безлимитные мессенджеры». Такие операторы есть в России, Беларуси, Казахстане и Армении.

        <b>На каких устройствах можно пользоваться ботом?</b>

        Почти на всех существующих! Вот список некоторых:

        <a href='https://itunes.apple.com/ru/app/telegram-messenger/id686449807'>Telegram для iOS</a>
        <a href='https://play.google.com/store/apps/details?id=org.telegram.messenger'>Telegram для Android</a>

        <a href='https://itunes.apple.com/ru/app/telegram/id747648890'>Telegram для MacOS</a>
        <a href='https://desktop.telegram.org/'>Telegram для Windows</a>
        <a href='https://desktop.telegram.org/'>Telegram для Linux</a>

        Надеемся, что смогли дать ответ на все ваши вопросы!
    """

    
    await message.answer(
        text = text,
        parse_mode="html",
        disable_web_page_preview=True
    )
    logger.info("Обработчик get_instruction завершил работу")
