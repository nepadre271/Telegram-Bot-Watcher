from datetime import datetime

from sqlalchemy import select
import pytz

from core.repositories.base import BaseRepository, BaseQueryExpression
from bot.database.models import PaymentsHistory
from bot.settings import settings


class PaymentHistoryRepository(BaseRepository):
    async def get(self, expression: BaseQueryExpression) -> PaymentsHistory | None:
        statement = select(PaymentsHistory).where(
            expression.complete()
        )
        query = await self.session.execute(statement)
        result = query.scalar()
        return result

    async def create(
            self, user_id: int, subscribe_id: int, **extra_data
    ) -> PaymentsHistory:
        history = PaymentsHistory(
            user_id=user_id,
            subscribe_id=subscribe_id,
            created_at=datetime.now(pytz.timezone(settings.timezone)),
            extra_data=extra_data
        )
        self.session.add(history)
        await self.session.commit()
        return history
