from datetime import datetime, timedelta

from sqlalchemy import select, func
import pytz

from bot.database.models.user import User, UserAction
from core.repositories.base import BaseRepository
from bot.settings import settings


class UserRepository(BaseRepository):
    async def create(self, id: int, username: str = "", invite_from: int | None = None) -> User:
        user = User(
            id=id,
            username=username,
            invite_from=invite_from
        )
        self.session.add(user)
        await self.session.commit()
        return user

    async def get(self, id: int = 0, invite_from: int | None = None) -> User:
        user = await self.session.get(User, id)
        if not user:
            user = await self.create(id, invite_from=invite_from)
        return user

    async def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        query = await self.session.execute(statement)
        user = query.scalar()
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

    async def update_username(self, user: User, username: str) -> str:
        user.username = username
        await self.session.commit()
        return user.username

    async def invites_count(self, user: User) -> int:
        statement = select(func.count(User.id)).where(User.invite_from == user.id)
        result = await self.session.execute(statement)
        count = result.scalar()
        return count

    async def change_admin_status(self, user: User, status: bool = True) -> bool:
        user.is_admin = status
        await self.session.commit()
        return user.is_admin


class UserActionRepository(BaseRepository):
    async def create(self, user_id: int, event_name: str, params: dict):
        action = UserAction(
            user_id=user_id,
            name=event_name[:128],
            params=params
        )
        self.session.add(action)
        await self.session.commit()
