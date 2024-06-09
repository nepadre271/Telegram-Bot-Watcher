from datetime import timedelta
import json
from typing import Any

from aiogram.utils.deep_linking import create_deep_link
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject
from aiogram import Router, Bot, F, types
from loguru import logger

from core.repositories import UserRepository, PaymentHistoryRepository, SubscribeRepository
from bot.containers import Container
from bot.settings import settings

router = Router()


@logger.catch()
@inject
async def process_buy_command(
        callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str,
        subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
):
    subscribe = await subscribe_repository.get(int(item_id))
    if subscribe.visible is False:
        await callback.message.answer("Данная подписка не доступна")
        return

    sub_time = int(timedelta(days=subscribe.days).total_seconds())
    await callback.bot.send_invoice(
        callback.message.chat.id,
        title="Подписка на бота",
        description=subscribe.name,
        provider_token=settings.telegram_payments_token,
        currency='rub',
        prices=[
            types.LabeledPrice(label=subscribe.name, amount=subscribe.amount * 100)
        ],
        start_parameter="101",
        payload=json.dumps({
            "id": callback.message.chat.id,
            "subscribe_time": sub_time,
            "subscribe_id": subscribe.id
        })
    )


@router.shipping_query()
async def process_shipping_query(shipping_query: types.ShippingQuery, bot: Bot):
    await bot.answer_shipping_query(shipping_query.id, ok=True)


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
@logger.catch()
@inject
async def process_successful_payment(
        message: types.Message, bot: Bot,
        user_repository: UserRepository = Provide[Container.user_repository],
        payment_history_repository: PaymentHistoryRepository = Provide[Container.payments_history_repository],
):
    logger.info(f"PAYMENT_SUCCESSFUL: USER:{message.chat.id} PAYLOAD:{message.successful_payment.invoice_payload}")
    payload = json.loads(message.successful_payment.invoice_payload)
    subscribe_id = payload["subscribe_id"]

    user = await user_repository.get(message.chat.id)
    sub_to = await user_repository.update_subscribe(
        user, subscribe_time=timedelta(seconds=payload["subscribe_time"])
    )
    await payment_history_repository.create(user.id, int(subscribe_id))

    await bot.send_message(
        message.chat.id,
        f"Подписка действительна до {sub_to.strftime('%d.%m.%Y %H:%M')}"
    )
