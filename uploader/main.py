from contextlib import asynccontextmanager
from typing import Annotated

from taskiq import TaskiqEvents, TaskiqDepends, Context, SimpleRetryMiddleware, TaskiqState
from taskiq_redis import RedisAsyncResultBackend, ListQueueBroker
from faststream.redis.fastapi import RedisRouter
from redis.asyncio import Redis, from_url
from aiogram.enums import ParseMode
from fastapi import FastAPI

from uploader.limiter import concurrency_limiter_handler
from core.schemes.uploader import UploadMovieRequest
from bot.keyboards.inline import create_movie_nav
from core.repositories.movie import KinoClubAPI
from uploader.settings import settings
from uploader import storage, service
from uploader.bot import bot_factory
from uploader.logger import logger


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
task_broker.with_middlewares(
    SimpleRetryMiddleware(
        default_retry_count=3
    ),
)


@task_broker.task(
    retry_on_error="true"
)
@concurrency_limiter_handler(limit_per_worker=settings.task_limit_per_worker)
async def upload_movie(
        data: UploadMovieRequest,
        context: Annotated[Context, TaskiqDepends()]
):
    logger.info(f"Start task with data: {data}")
    await movie_storage.set(f"task:{data.get_movie_id()}", context.message.task_id)

    kinoclub_api = KinoClubAPI(settings.kinoclub_token, redis)
    movie = await kinoclub_api.get_movie(data.movie_id, disable_cache=True)

    # Загрузить и преобразовать файл
    file_path = await service.download_video(movie, data)

    # Сохранить в telegram
    file_id = await service.upload_video_to_telegram(movie, data, file_path)

    # Удалить временный файл
    service.remove_folder(file_path.parent)

    await movie_storage.set(data.get_movie_id(), file_id)

    logger.info(f"Movie[{data.movie_id}] uploaded in telegram, {file_id=}")
    data.file_id = file_id
    data = data.model_dump_json()
    await message_router.broker.publisher(
        channel="movie_uploaded"
    ).publish(data)


async def send_notification(data: str):
    data: UploadMovieRequest = UploadMovieRequest.model_validate_json(data)
    kinoclub_api = KinoClubAPI(settings.kinoclub_token, redis)
    movie = await kinoclub_api.get_movie(data.movie_id)
    skip_users = dict()
    bot = bot_factory()

    reply_markup = create_movie_nav(movie, data)

    if movie.type == "film":
        caption = f"<b>{movie.name}</b>"
    else:
        caption = (f"<b>{movie.name}</b> \nСезон: {data.season} "
                   f"Серия: {data.seria} из {len(movie.seasons[data.season-1].series)}")

    caption = "\n\n".join((
        caption, f"Смотрите любимые сериалы в {settings.telegram_bot_id}"
    ))
    while (await users_queue.length(data.get_movie_id())) > 0:
        try:
            user_id = await users_queue.pop(data.get_movie_id())
        except IndexError:
            break

        if user_id is None or skip_users.get(user_id, None):
            continue

        skip_users[user_id] = 1
        try:
            await bot.send_video(
                user_id, data.file_id,
                supports_streaming=True, width=1280, height=720,
                caption=caption, reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
            )
            logger.debug(f"Send video[{data.file_id}] for user[{user_id}]")
        finally:
            pass

    await bot.session.close()


@task_broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(state: TaskiqState):
    await message_router.broker.start()


@task_broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(state: TaskiqState):
    await redis.aclose()


@asynccontextmanager
async def lifespan(app: FastAPI):
    message_router.subscriber("movie_uploaded")(send_notification)
    async with message_router.lifespan_context(app):
        yield


app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def process_request(data: UploadMovieRequest):
    await users_queue.add(data.get_movie_id(), data.user_id)
    logger.info(f"Add user:{data.user_id} to queue Movie[{data.movie_id}]")

    file_id = await movie_storage.get(data.get_movie_id())
    if file_id is not None:
        logger.info(f"Movie[{data.get_movie_id()}] found in storage, {file_id=}")
        data.file_id = file_id
        data = data.model_dump_json()
        await movie_publisher.publish(data)
        return

    bot = bot_factory()
    logger.info(f"Movie[{data.get_movie_id()}] not found in storage")

    movie_type_verbose = {
        "film": "фильм",
        "serial": "серию"
    }
    await bot.send_message(data.user_id, f"Загружаю {movie_type_verbose[data.type.value]}, это займет некоторое время")

    task_id = await movie_storage.get(f"task:{data.get_movie_id()}")
    if task_id:
        ready = await task_backend.is_result_ready(task_id)
        if ready is False:
            return

        task = await task_backend.get_result(task_id)
        if task.is_err:
            logger.info(f"Error in task[{task_id}] -> {task.error}")
            await movie_storage.delete(f"task:{data.get_movie_id()}")
        else:
            file_id = task.return_value
            data.file_id = file_id
            data = data.model_dump_json()
            await movie_publisher.publish(data)
            return

    task = await upload_movie.kiq(data)

    logger.info(f"Task[{task.task_id}] start upload Movie[{data.get_movie_id()}] to telegram")
    await bot.session.close()
