from uuid import uuid4

from ayoomoney import YooMoneyWalletAsync
from aiogram.types import CallbackQuery
from sqlalchemy import String
from aiogram import Router, Dispatcher
from loguru import logger

from .base import BaseSubscribePayment
from bot.keyboards.inline import create_yoomoney_subscribe_block
from bot.database.models import Subscribe, PaymentsHistory
from bot.schemes import YooMoneySubscribeCallbackFactory
from core.repositories.base import BaseQueryExpression
from bot.settings import settings

router = Router()
payment_logger = logger.bind(payments=True)


class YooMoneySubscribePayment(BaseSubscribePayment):
    router = router

    def registry_router(self, dp: Dispatcher):
        from bot.handlers.user.payment import yoomoney_router
        self.router = yoomoney_router
        super().registry_router(dp)

    def __init__(self, client: YooMoneyWalletAsync):
        self.client = client

    async def execute(self, subscribe: Subscribe, *args, **kwargs):
        callback: CallbackQuery = kwargs.get("callback")
        if settings.service.disable_sub_system:
            await callback.message.answer(
                "В данный момент возможность приобрести подписку недоступна, попробуйте позже"
            )
            return

        label = str(uuid4())
        form = await self.client.create_payment_form(
            subscribe.amount,
            unique_label=label,
            success_redirect_url=f"https://t.me/{settings.telegram.bot_id[1:]}"
        )

        callback_data = YooMoneySubscribeCallbackFactory(
            label=label,
            sub_id=subscribe.id
        ).pack()

        await callback.bot.send_message(
            callback.message.chat.id,
            "Подписка на бота",
            reply_markup=create_yoomoney_subscribe_block(form.link_for_customer, callback_data)
        )


class GetHistoryByLabelExpression(BaseQueryExpression):
    def __init__(self, label: str):
        self.label = label

    def complete(self):
        return PaymentsHistory.extra_data['label'].astext.cast(String) == self.label
