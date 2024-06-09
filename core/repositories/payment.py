from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from bot.database.models import PaymentsHistory
from bot.settings import settings


class PaymentHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def __del__(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.session.aclose(), loop=loop)

    async def create(self, user_id: int, subscribe_id: int) -> PaymentsHistory:
        history = PaymentsHistory(
            user_id=user_id,
            subscribe_id=subscribe_id,
            created_at=datetime.now(pytz.timezone(settings.timezone))
        )
        self.session.add(history)
        await self.session.commit()
        return history
