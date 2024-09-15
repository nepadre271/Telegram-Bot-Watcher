from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject
from aiogram import Router
from loguru import logger

from core.repositories import SubscribeRepository
from bot.payment import BaseSubscribePayment
from bot.containers import Container
from bot.settings import settings
from bot.utils import tracker

router = Router()
payment_logger = logger.bind(payments=True)


@logger.catch()
@tracker("Subscribe: process buy command")
@inject
async def process_buy_command(
        callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
        payment: BaseSubscribePayment = Provide[Container.payment],
        **kwargs
):
    if settings.service.disable_sub_system is True:
        await callback.message.answer("В данный момент возможность приобрести подписку недоступна, попробуйте позже")
        return

    subscribe = await subscribe_repository.get(int(item_id))
    if subscribe.visible is False:
        await callback.message.answer("Данная подписка не доступна")
        return

    if settings.payment.service == "telegram":
        await payment.execute(subscribe, callback=callback)
    elif settings.payment.service == "yoomoney":
        await payment.execute(subscribe, callback=callback)
