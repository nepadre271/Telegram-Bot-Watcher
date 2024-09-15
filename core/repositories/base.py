import asyncio

from sqlalchemy.sql._typing import _ColumnExpressionArgument
from sqlalchemy.ext.asyncio import AsyncSession


class BaseQueryExpression:
    def complete(self) -> _ColumnExpressionArgument[bool]:
        raise NotImplementedError


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def __del__(self):
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.session.aclose(), loop=loop)
