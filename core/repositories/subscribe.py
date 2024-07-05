from sqlalchemy.sql import select

from bot.database.models.subscribe import Subscribe
from core.repositories.base import BaseRepository


class SubscribeRepository(BaseRepository):
    async def create(self, days: int, amount: int, name: str) -> Subscribe:
        subscribe = Subscribe(
            days=days,
            amount=amount,
            name=name
        )
        self.session.add(subscribe)
        await self.session.commit()
        return subscribe

    async def get(self, id: int) -> Subscribe | None:
        subscribe = await self.session.get(Subscribe, id)
        await self.session.commit()
        return subscribe

    async def all(self) -> list[Subscribe]:
        statement = select(Subscribe).where(Subscribe.visible == True)
        query = await self.session.execute(statement)
        return [subscribe[0] for subscribe in query.all()]

    async def toggle_visibility(self, subscribe: Subscribe):
        subscribe.visible = not subscribe.visible
        await self.session.commit()

    async def update_price(self, subscribe: Subscribe, amount: int):
        subscribe.amount = amount
        await self.session.commit()
