from contextlib import asynccontextmanager
from typing import Annotated
import logging

from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from taskiq import TaskiqEvents, TaskiqDepends, Context
from faststream.redis.fastapi import RedisRouter
from redis.asyncio import Redis, from_url
from fastapi import FastAPI

from uploader import schemes, storage, service
from uploader.settings import settings
from uploader.bot import bot_factory
from core.services.movie import KinoClubAPI

redis: Redis = from_url(settings.redis_dsn, decode_responses=True)
users_queue = storage.Queue(redis, "UserQueue")
movie_storage = storage.Storage(redis, "MovieStorage")
message_router = RedisRouter(settings.redis_dsn)
movie_publisher = message_router.broker.publisher("movie_uploaded")
task_backend = RedisAsyncResultBackend(
    redis_url=settings.redis_dsn,
)
task_broker = ListQueueBroker(
    url=settings.redis_dsn
)
task_broker.with_result_backend(task_backend)

logger = logging.getLogger(__name__)
    

@task_broker.task
async def upload_movie(
    movie_id: int,
    context: Annotated[Context, TaskiqDepends()]
):
    await movie_storage.set(f"task:{movie_id}", context.message.task_id)
        
    kinoclub_api = KinoClubAPI(settings.kinoclub_token, redis)
    movie = await kinoclub_api.get_movie(movie_id)
    
    # Загрузить и преобразовать файл
    file_path = await service.download_video(movie)
        
    # Сохранить в telegram
    file_id = await service.upload_video_to_telegram(movie, file_path)
    
    # Удалить временный файл
    service.remove_folder(file_path.parent)
    
    await movie_storage.set(movie_id, file_id)
    
    logger.info(f"Movie[{movie_id}] uploaded in telegram, {file_id=}")
    data = schemes.UploadMovieData(file_id=file_id, movie_id=movie_id)
    data = data.model_dump_json()
    await message_router.broker.publisher(
        channel="movie_uploaded"
    ).publish(data)
    

async def send_notification(data: str):
    data: schemes.UploadMovieData = schemes.UploadMovieData.model_validate_json(data)
        
    skip_users = dict()
    bot = bot_factory()
    while (await users_queue.length(data.movie_id)) > 0:
        try:
            user_id = await users_queue.pop(data.movie_id)
        except IndexError:
            break
        
        if user_id is None or skip_users.get(user_id, None):
            continue
        
        skip_users[user_id] = 1
        try:
            await bot.send_video(user_id, data.file_id, supports_streaming=True)
            logger.info(f"Send video[{data.file_id}] for user[{user_id}]")
        finally:
            pass
        
    await bot.close()


@task_broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(_):
    await message_router.broker.start()


@task_broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(_):
    await redis.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    message_router.subscriber("movie_uploaded")(send_notification)
    async with message_router.lifespan_context(app):
        yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def process_request(data: schemes.MovieRequest):
    await users_queue.add(data.movie_id, data.user_id)
    logger.info(f"Add user:{data.user_id} to queue Movie[{data.movie_id}]")
    
    file_id = await movie_storage.get(data.movie_id)
    if file_id is not None:
        logger.info(f"Movie[{data.movie_id}] found in storage, {file_id=}")
        data = schemes.UploadMovieData(file_id=file_id, movie_id=data.movie_id)
        data = data.model_dump_json()
        await send_notification(data)
        await movie_publisher.publish(data)
        return
        
    logger.info(f"Movie[{data.movie_id}] not found in storage")
    
    task_id = await movie_storage.get(f"task:{data.movie_id}")
    if task_id:
        ready = await task_backend.is_result_ready(task_id)
        if ready is False:
            return
        
        task = await task_backend.get_result(task_id)
        if task.is_err:
            logger.info(f"Error in task[{task_id}] -> {task.error}")
            await movie_storage.delete(f"task:{data.movie_id}")
        else:
            file_id = task.return_value
            data = schemes.UploadMovieData(movie_id=data.movie_id, file_id=file_id).model_dump_json()
            await send_notification(data)
            return
        
    task = await upload_movie.kiq(data.movie_id)
    
    logger.info(f"Task[{task.task_id}] start upload Movie[{data.movie_id}] to telegram")
