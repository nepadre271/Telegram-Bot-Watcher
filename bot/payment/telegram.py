from datetime import timedelta
import json

from aiogram.types import CallbackQuery
from aiogram import Router, types, Dispatcher
from loguru import logger

from bot.database.models import Subscribe
from .base import BaseSubscribePayment
from bot.settings import settings

router = Router()
payment_logger = logger.bind(payments=True)


class TelegramSubscribePayment(BaseSubscribePayment):
    router = router

    def registry_router(self, dp: Dispatcher):
        from bot.handlers.user.payment import telegram_router
        self.router = telegram_router
        super().registry_router(dp)

    async def execute(self, subscribe: Subscribe, *args, **kwargs):
        callback: CallbackQuery = kwargs.get("callback")

        sub_time = int(timedelta(days=subscribe.days).total_seconds())
        await callback.bot.send_invoice(
            callback.message.chat.id,
            title="Подписка на бота",
            description=subscribe.name,
            provider_token=settings.payment.telegram_token,
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
