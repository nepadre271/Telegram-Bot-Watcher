from dependency_injector.wiring import inject, Provide
from redis.asyncio import Redis
from aiogram import Router, types
from loguru import logger

from bot.schemes import PageCallbackFactory, UploadMovieCallbackFactory
from core.services import UploaderService, MovieService
from bot.keyboards.inline import create_movie_buttons
from core.schemes.uploader import UploadMovieRequest
from bot.containers import Container

router = Router()
        

@router.callback_query(PageCallbackFactory.filter())
@inject
async def process_page(
    query: types.CallbackQuery, 
    callback_data: PageCallbackFactory, 
    movie_service: MovieService = Provide[Container.movie_service],
    redis: Redis = Provide[Container.redis_client]
):
    search_query = await redis.hget("query-table", callback_data.query_hash)
    data = await movie_service.search(search_query, callback_data.number)
    if data is None:
        return
    
    inline_kb = create_movie_buttons(data, callback_data.query_hash)
    await query.message.edit_text("Выберите фильм или сериал из списка ниже:", reply_markup=inline_kb)


@router.callback_query(UploadMovieCallbackFactory.filter())
@logger.catch()
@inject
async def process_movie_callback(
    query: types.CallbackQuery,
    callback_data: UploadMovieCallbackFactory,
    movie_service: MovieService = Provide[Container.movie_service],
    uploader_service: UploaderService = Provide[Container.uploader_service]
):
    movie = await movie_service.get(callback_data.id)

    if movie is None:
        logger.error(f"Данные о фильме отсутствуют ID:{callback_data.id}")
        await query.message.answer("Извините, информация о фильме не найдена.")
        return
    
    data = UploadMovieRequest(
        user_id=query.message.chat.id,
        movie_id=movie.id,
        type=movie.type,
        season=callback_data.season,
        seria=callback_data.seria
    )
    try:
        await uploader_service.upload_movie(data)
    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        return
