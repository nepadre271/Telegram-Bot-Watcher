from datetime import datetime, timedelta
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import pytz

from bot.database.models.user import User
from bot.settings import settings


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def __del__(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.session.aclose(), loop=loop)

    async def create(self, id: int, invite_from: int | None = None) -> User:
        user = User(
            id=id,
            invite_from=invite_from
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def get(self, id: int, invite_from: int | None = None) -> User:
        user = await self.session.get(User, id)
        if not user:
            user = await self.create(id, invite_from)
        await self.session.commit()
        return user

    async def get_by_ref(self, ref: str) -> User | None:
        statement = select(User).where(User.ref == ref)
        query = await self.session.execute(statement)
        user = query.scalar()
        return user

    async def exists(self, id: int) -> bool:
        statement = select(User.id).where(User.id == id).exists()
        query = await self.session.execute(select(statement))
        return query.scalar()

    async def group_subscribe_toggle(self, user: User):
        user.join_to_group = datetime.now(pytz.timezone(settings.timezone))
        await self.session.commit()

    async def update_subscribe(self, user: User, subscribe_time: timedelta) -> datetime:
        subscribe_start_from = datetime.now(pytz.timezone(settings.timezone))
        if not user.is_subscribe_expire():
            subscribe_start_from = user.subscribe_expire

        user.subscribe_expire = subscribe_start_from + subscribe_time
        await self.session.commit()
        return user.subscribe_expire

    async def update_views_count(self, user: User, amount: int) -> int:
        user.views_left = user.views_left + amount
        await self.session.commit()
        return user.views_left

    async def invites_count(self, user: User) -> int:
        statement = select(func.count(User.id)).where(User.invite_from == user.ref)
        result = await self.session.execute(statement)
        count = result.scalar()
        return count

    # async def update_user_data(self, id: int, page: int) -> User:
    #     user = await self.session.get(User, id)
    #     user.page = page
    #
    #     await self.session.commit()
    #     return user
    #
    # async def delete_bookmark(self, user_id: int, page: int):
    #     stmt = delete(Bookmark).where(
    #         and_(user_id == Bookmark.user_id, page == Bookmark.page)
    #     )
    #     await self.session.execute(stmt)
    #     await self.session.commit()
    #
    # async def get_all_bookmarks(self, user_id) -> List[int]:
    #     stmt = select(Bookmark.page).where(Bookmark.user_id == user_id)
    #     result = await self.session.execute(stmt)
    #     result = [i[0] for i in result.all()]
    #     return result