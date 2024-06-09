from datetime import timedelta, datetime
import asyncio
import logging
import json
import uuid

from aiogram import Bot, types, Dispatcher, filters, F

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot("6614907779:AAEt-uR3TN2A3aQpHmcugijz-vHqS4dWAAw")
dp = Dispatcher(loop=loop)

# Setup prices
PRICES = [
    types.LabeledPrice(label='Настоящая Машина Времени', amount=42000),
    types.LabeledPrice(label='Подарочная упаковка', amount=30000)
]


@dp.message(filters.Command('buy'))
async def process_buy_command(message: types.Message):
    sub_time = int(timedelta(days=1).total_seconds())
    await bot.send_invoice(
        message.chat.id,
        title="Подписка на бота",
        description="1 месяц",
        provider_token="381764678:TEST:85246",
        currency='rub',
        prices=PRICES,
        start_parameter='time-machine-example',
        payload=json.dumps({
            "id": str(uuid.uuid4()),
            "sub_time": sub_time
        })
    )


@dp.shipping_query()
async def process_shipping_query(shipping_query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query.id, ok=True)


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    payload = json.loads(message.successful_payment.invoice_payload)
    sub_to = datetime.now() + timedelta(seconds=payload["sub_time"])
    await bot.send_message(
        message.chat.id,
        f"Подписка действительна до {sub_to.strftime('%d.%m.%Y %H:%M')}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop.run_until_complete(main())
