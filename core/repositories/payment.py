from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
import pytz

from core.repositories.base import BaseRepository
from bot.database.models import PaymentsHistory
from bot.settings import settings


class PaymentHistoryRepository(BaseRepository):
    async def create(
            self, user_id: int, subscribe_id: int,
            telegram_payment_charge_id: str,
            provider_payment_charge_id: str
    ) -> PaymentsHistory:
        history = PaymentsHistory(
            user_id=user_id,
            subscribe_id=subscribe_id,
            telegram_payment_charge_id=telegram_payment_charge_id,
            provider_payment_charge_id=provider_payment_charge_id,
            created_at=datetime.now(pytz.timezone(settings.timezone))
        )
        self.session.add(history)
        await self.session.commit()
        return history
