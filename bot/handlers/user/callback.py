import logging

from aiogram import Router, types, Bot

from core.services.movie import KinoClubAPI, UploaderService
from bot.keyboards.inline import create_movie_buttons
from bot.handlers.user.search import kp_api
from bot.database.redis import redis
from bot.settings import settings

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query()
async def process_callback(query: types.CallbackQuery, bot: Bot):
    data = query.data
    logger.info(f"{query.data=}")
    if data == 'pages:next_page':
        await next_page(query)
    elif data == 'pages:prev_page':
        await prev_page(query)
    elif data.startswith("movie:"):
        await process_movie_callback(query)


async def next_page(query: types.CallbackQuery):
    logger.info("Обработчик next_page вызван")
    if kp_api.current_index + 10 < len(kp_api.results):
        kp_api.current_index += 10
        results = kp_api.results[kp_api.current_index:kp_api.current_index + 10]
        inline_kb = create_movie_buttons(results, kp_api.current_index, len(kp_api.results))
        await query.message.edit_text("Выберите фильм или сериал из списка ниже:", reply_markup=inline_kb)
        logger.info("Обработчик next_page обработал callback следующей страницы")


async def prev_page(query: types.CallbackQuery):
    logger.info("Обработчик prev_page вызван")
    if kp_api.current_index >= 10:
        kp_api.current_index -= 10
        results = kp_api.results[kp_api.current_index:kp_api.current_index + 10]
        inline_kb = create_movie_buttons(results, kp_api.current_index, len(kp_api.results))
        await query.message.edit_text("Выберите фильм или сериал из списка ниже:", reply_markup=inline_kb)
        logger.info("Обработчик prev_page обработал callback предыдущей страницы")


async def process_movie_callback(query: types.CallbackQuery):
    logger.info("Обработчик process_movie_callback вызван")
    movie_id = query.data.split(":")[1]

    try:
        kinoclub_api = KinoClubAPI(settings.kinoclub_token, redis)
        movie = await kinoclub_api.get_movie(movie_id)
    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        return

    if movie is None:
        logger.error("Данные о фильме отсутствуют или не содержат ключ 'data'")
        await query.message.answer("Извините, информация о фильме не найдена.")
        return

    if movie.type == "film":
        try:
            uploader = UploaderService(settings.uploader_url)
            await uploader.upload_movie(query.message.chat.id, movie_id)
        except Exception as ex:
            logger.error(str(ex), exc_info=True)
            return
        
    elif movie.type == "serial":
        seasons_dict = {}
        for season in movie.seasons:
            series_dict = {}
            for seria in season.series:
                series_dict[seria.number] = seria.download_url
            seasons_dict[season.title] = series_dict

    message_text = f"<b>{movie.type.verbose}</b>: {movie.name}\\n\\n<b>Описание</b>:\\n{movie.full_description}"

    logger.info(
        f"Обработчик process_movie_callback отправил сообщение с информацией о '{movie.name}' (id:{movie.id})")
    await query.message.answer_photo(photo=str(movie.poster), caption=message_text, parse_mode="html")
