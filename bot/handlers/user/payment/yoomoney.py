from datetime import timedelta

from dependency_injector.wiring import Provide, inject
from ayoomoney import YooMoneyWalletAsync
from aiogram import Router, types
from loguru import logger

from core.repositories import UserRepository, PaymentHistoryRepository, SubscribeRepository
from bot.payment.yoomoney import GetHistoryByLabelExpression
from bot.schemes import YooMoneySubscribeCallbackFactory
from bot.containers import Container
from bot.utils import tracker

router = Router()
payment_logger = logger.bind(payments=True)


@router.callback_query(YooMoneySubscribeCallbackFactory.filter())
@tracker("Subscribe: YooMoney check payment")
@logger.catch()
@inject
async def check_payment_callback(
    query: types.CallbackQuery,
    callback_data: YooMoneySubscribeCallbackFactory,
    user_repository: UserRepository = Provide[Container.user_repository],
    subscribe_repository: SubscribeRepository = Provide[Container.subscribe_repository],
    payment_history_repository: PaymentHistoryRepository = Provide[Container.payments_history_repository],
    yoomoney_client: YooMoneyWalletAsync = Provide[Container.yoomoney_client],
    **kwargs
):
    payment_is_completed: bool = await yoomoney_client.check_payment_on_successful(callback_data.label)
    if payment_is_completed is False:
        await query.message.answer(
            "Подписка не оплачена."
        )
        return

    history = await payment_history_repository.get(
        GetHistoryByLabelExpression(label=callback_data.label)
    )
    logger.info(history)
    if history:
        await query.message.answer(
            "Подписка оплачена и применена."
        )
        return

    subscribe = await subscribe_repository.get(callback_data.sub_id)
    sub_time = int(timedelta(days=subscribe.days).total_seconds())

    user = await user_repository.get(query.from_user.id)

    sub_to = await user_repository.update_subscribe(
        user, subscribe_time=timedelta(seconds=sub_time)
    )
    await payment_history_repository.create(
        user.id, int(subscribe.id),
        service="yoomoney",
        label=callback_data.label
    )

    await query.message.answer(
        f"Подписка действительна до {sub_to.strftime('%d.%m.%Y %H:%M')}"
    )
    payment_logger.info(
        f"PAYMENT_SUCCESSFUL_EXIT: USER:{query.from_user.id} "
        "Service: Yoomoney "
        f"AMOUNT:{subscribe.amount} "
    )
