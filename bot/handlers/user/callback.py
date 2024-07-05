from dependency_injector.wiring import inject, Provide
from aiogram import Router, types, Bot
from loguru import logger

from core.services import UploaderService, MovieService
from core.schemes.uploader import UploadMovieRequest
from bot.schemes import UploadMovieCallbackFactory
from bot.keyboards.inline import create_sub_block
from bot.utils import is_user_subscribed, tracker
from core.repositories import UserRepository
from bot.database.models.user import User
from bot.containers import Container
from bot.settings import settings

router = Router()


def can_watch(func):
    @inject
    async def wrapper(
            query: types.CallbackQuery,
            callback_data: UploadMovieCallbackFactory,
            user_repository: UserRepository = Provide[Container.user_repository],
            **kwargs
    ):
        user_data = query.message.chat
        bot: Bot = kwargs.get("bot")
        user: User = kwargs.get("user")
        if kwargs.get("is_admin", False):
            logger.debug(f"Admin: User[{user_data.username}] can watch")
            return await func(query, callback_data, **kwargs)

        text = ["Для продолжения бесплатного просмотра подпишитесь на группы:"]
        check_sub_chats = []
        for chat_id in settings.telegram.chats_id:
            joined = await is_user_subscribed(bot, user.id, chat_id)
            check_sub_chats.append(joined)
            text.append(f"{'✔' if joined else '❌'} {chat_id}")

        if all(check_sub_chats) is False:
            markup = create_sub_block(callback_data.pack())
            await query.message.answer("\n".join(text), reply_markup=markup)
            return

        if settings.disable_sub_system:
            return await func(query, callback_data, **kwargs)

        if user.join_to_group is None and all(check_sub_chats):
            await user_repository.group_subscribe_toggle(user)
            await user_repository.update_views_count(user, 20)
            logger.debug(f"Пользователь[{user_data.username}:{user_data.id}] подписался на группы")

        if user.is_subscribe_expire() and user.views_left <= 0:
            await query.message.answer("Чтобы продолжить просмотр, оформите подписку или пригласите друга.")
            return

        return await func(query, callback_data, **kwargs)
    return wrapper


@router.callback_query(UploadMovieCallbackFactory.filter())
@tracker("Movie: process upload")
@can_watch
@logger.catch()
@inject
async def process_movie_callback(
    query: types.CallbackQuery,
    callback_data: UploadMovieCallbackFactory,
    movie_service: MovieService = Provide[Container.movie_service],
    uploader_service: UploaderService = Provide[Container.uploader_service],
    user_repository: UserRepository = Provide[Container.user_repository],
    **kwargs
):
    movie = await movie_service.get(callback_data.id)

    if movie is None:
        logger.error(f"Данные о фильме отсутствуют ID:{callback_data.id}")
        await query.message.answer("Извините, информация о фильме не найдена.")
        return

    tracker_data = kwargs.get("tracker_data", {})
    tracker_data["movie_name"] = movie.name
    tracker_data["movie_id"] = movie.id
    for line in movie.full_description.split("\n"):
        if "Год выпуска:" in line:
            tracker_data["year"] = line.replace("Год выпуска:", "").strip()
            break
    tracker_data["type"] = movie.type.value
    if movie.type.value == "serial":
        tracker_data["season"] = callback_data.season
        tracker_data["seria"] = callback_data.seria

    user: User = kwargs.get("user")
    if user.views_left > 0 and user.is_subscribe_expire():
        await user_repository.update_views_count(user, -1)

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
