from datetime import timedelta
from typing import Any
import json

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from dependency_injector.wiring import Provide, inject
from aiogram import Router, Bot, F, types
from loguru import logger

from core.repositories import UserRepository, PaymentHistoryRepository, SubscribeRepository
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
        **kwargs
):
    if settings.disable_sub_system is True:
        await callback.message.answer("В данный момент возможность приобрести подписку недоступна, попробуйте позже")
        return

    subscribe = await subscribe_repository.get(int(item_id))
    if subscribe.visible is False:
        await callback.message.answer("Данная подписка не доступна")
        return

    sub_time = int(timedelta(days=subscribe.days).total_seconds())
    await callback.bot.send_invoice(
        callback.message.chat.id,
        title="Подписка на бота",
        description=subscribe.name,
        provider_token=settings.telegram.payments_token,
        currency='rub',
        prices=[
            types.LabeledPrice(label=subscribe.name, amount=subscribe.amount * 100)
        ],
        start_parameter="101",
        payload=json.dumps({
            "id": callback.message.chat.id,
            "subscribe_time": sub_time,
            "subscribe_id": subscribe.id
        }),
        protect_content=True
    )


@router.shipping_query(flags={"skip_user_middleware": True})
async def process_shipping_query(shipping_query: types.ShippingQuery, bot: Bot):
    await bot.answer_shipping_query(shipping_query.id, ok=True)


@router.pre_checkout_query(flags={"skip_user_middleware": True})
@tracker("Subscribe: pre checkout query")
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery, bot: Bot, **kwargs):
    if settings.disable_sub_system is True:
        try:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id, ok=False,
                error_message="В данный момент возможность приобрести подписку недоступна, попробуйте позже"
            )
        finally:
            return

    try:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    finally:
        payment_logger.info(
            f"PAYMENT_PRE_CHECKOUT: USER:{pre_checkout_query.from_user.id} "
            f"AMOUNT:{pre_checkout_query.total_amount // 100} "
            f"PAYLOAD:{pre_checkout_query.invoice_payload} "
        )


@router.message(F.successful_payment, flags={"skip_user_middleware": True})
@tracker("Subscribe: process successful payment")
@logger.catch()
@inject
async def process_successful_payment(
        message: types.Message, bot: Bot,
        user_repository: UserRepository = Provide[Container.user_repository],
        payment_history_repository: PaymentHistoryRepository = Provide[Container.payments_history_repository],
        **kwargs
):
    payment_logger.info(
        f"PAYMENT_SUCCESSFUL_ENTER: USER:{message.chat.id} "
        f"AMOUNT:{message.successful_payment.total_amount // 100} "
        f"PAYLOAD:{message.successful_payment.invoice_payload} "
        f"TELEGRAM_PAYMENT_CHARGE_ID:{message.successful_payment.telegram_payment_charge_id} "
        f"PROVIDER_PAYMENT_CHARGE_ID:{message.successful_payment.provider_payment_charge_id} "
    )
    payload = json.loads(message.successful_payment.invoice_payload)
    subscribe_id = payload["subscribe_id"]

    user = await user_repository.get(message.chat.id)
    sub_to = await user_repository.update_subscribe(
        user, subscribe_time=timedelta(seconds=payload["subscribe_time"])
    )
    await payment_history_repository.create(
        user.id, int(subscribe_id),
        message.successful_payment.telegram_payment_charge_id,
        message.successful_payment.provider_payment_charge_id
    )

    await bot.send_message(
        message.chat.id,
        f"Подписка действительна до {sub_to.strftime('%d.%m.%Y %H:%M')}"
    )
    payment_logger.info(
        f"PAYMENT_SUCCESSFUL_EXIT: USER:{message.chat.id} "
        f"AMOUNT:{message.successful_payment.total_amount // 100} "
        f"PAYLOAD:{message.successful_payment.invoice_payload} "
        f"TELEGRAM_PAYMENT_CHARGE_ID:{message.successful_payment.telegram_payment_charge_id} "
        f"PROVIDER_PAYMENT_CHARGE_ID:{message.successful_payment.provider_payment_charge_id} "
    )
