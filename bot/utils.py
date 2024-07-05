import asyncio
from functools import wraps

from dependency_injector.wiring import inject, Provide
from aiogram.exceptions import TelegramBadRequest
from aiogram_dialog import DialogManager
from aiogram import Bot, types

from core.repositories.user import UserActionRepository
from bot.database.models import User
from bot.containers import Container
from bot.settings import settings


async def is_user_subscribed(bot: Bot, user_id: int, channel_id: str) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except TelegramBadRequest:
        return False


def check_admin_status(user: User) -> bool:
    return any([
        user.id in settings.telegram.admins,
        user.is_admin,
    ])


def only_admin_handler(func):
    @wraps(func)
    async def wrapper(
            *args, **kwargs
    ):
        is_admin = kwargs.get("is_admin", False)

        if is_admin:
            return await func(*args, **kwargs)
        return

    return wrapper


def tracker(name: str):
    def inner(func):
        @inject
        async def wrapper(
                *args,
                user_action_repository: UserActionRepository = Provide[Container.user_action_repository],
                **kwargs
        ):
            tracker_data = {}
            kwargs["tracker_data"] = tracker_data
            if len(args) > 0:
                query = args[0]
            else:
                query = kwargs.get("dialog_manager", 0)

            try:
                return await func(*args, **kwargs)
            finally:
                user = None
                params = {}
                if isinstance(query, types.CallbackQuery):
                    user = query.message.chat.id
                    params["type"] = "Callback"
                    params["callback_data"] = query.data

                elif isinstance(query, types.Message):
                    user = query.chat.id
                    params["type"] = "Message"
                    params["text"] = query.text
                    if query.successful_payment:
                        params["type"] = "SuccessfulPayment"
                        params["successful_payment"] = query.successful_payment.model_dump()
                        del params["text"]

                elif isinstance(query, types.PreCheckoutQuery):
                    user = query.from_user.id
                    params["type"] = "PreCheckoutQuery"
                    params["callback_data"] = query.model_dump()

                elif "aiogram_dialog" in str(type(query)):
                    query: DialogManager
                    user = query.event.from_user.id
                    params["type"] = "DialogHandler"
                    params["dialog_data"] = query.dialog_data

                if user is not None:
                    if tracker_data:
                        params["extra"] = tracker_data
                    asyncio.create_task(user_action_repository.create(
                        user_id=user,
                        event_name=name,
                        params=params
                    ))

        return wrapper

    return inner
