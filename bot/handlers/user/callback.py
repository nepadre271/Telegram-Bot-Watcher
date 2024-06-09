from dependency_injector.wiring import inject, Provide
from aiogram import Router, types, Bot
from loguru import logger

from bot.keyboards.inline import create_sub_block
from bot.utils import is_user_subscribed
from core.services import UploaderService, MovieService
from core.schemes.uploader import UploadMovieRequest
from bot.schemes import UploadMovieCallbackFactory
from core.repositories import UserRepository
from bot.containers import Container
from bot.settings import settings
from bot.utils import check_admin_status

router = Router()


def can_watch(func):
    @inject
    async def wrapper(
            query: types.CallbackQuery,
            callback_data: UploadMovieCallbackFactory,
            bot: Bot,
            user_repository: UserRepository = Provide[Container.user_repository],
            **kwargs
    ):
        user_data = query.message.chat

        user = await user_repository.get(user_data.id)
        if check_admin_status(user):
            logger.debug(f"Admin: User[{user_data.username}] can watch")
            return await func(query, callback_data, bot, **kwargs)

        check_sub_chat = await is_user_subscribed(bot, user.id, settings.chat_id)
        if check_sub_chat is False:
            text = "Для продолжения бесплатного просмотра подпишитесь на группу"
            markup = create_sub_block(callback_data.pack())
            await query.message.answer(text, reply_markup=markup)
            return

        if user.join_to_group is None and check_sub_chat:
            await user_repository.group_subscribe_toggle(user)
            await user_repository.update_views_count(user, 20)
            logger.debug(f"Пользователь[{user_data.username}:{user_data.id}] подписался на группу")

        if user.is_subscribe_expire() and user.views_left <= 0:
            await query.message.answer("Кина не будет 🌚👍\nПригласи друга или купи подписку")
            return

        return await func(query, callback_data, bot, **kwargs)
    return wrapper


@router.callback_query(UploadMovieCallbackFactory.filter())
@can_watch
@logger.catch()
@inject
async def process_movie_callback(
    query: types.CallbackQuery,
    callback_data: UploadMovieCallbackFactory,
    bot: Bot,
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

    await query.message.answer("Кина будет 🌚👍")
    user = await user_repository.get(query.message.chat.id)
    if user.views_left > 0:
        await user_repository.update_views_count(user, -1)
    # data = UploadMovieRequest(
    #     user_id=query.message.chat.id,
    #     movie_id=movie.id,
    #     type=movie.type,
    #     season=callback_data.season,
    #     seria=callback_data.seria
    # )
    # try:
    #     await uploader_service.upload_movie(data)
    # except Exception as ex:
    #     logger.error(str(ex), exc_info=True)
    #     return
