import uuid
from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import pytz

from bot.database.models.base import Base, GUID
from bot.settings import settings


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    join = Column(DateTime(timezone=True), server_default=func.now())
    join_to_group = Column(DateTime(timezone=True), nullable=True, default=None)
    subscribe_expire = Column(DateTime(timezone=True), nullable=True, default=None)
    is_admin = Column(Boolean, default=False)

    ref = Column(GUID(), default=lambda: str(uuid.uuid4()), index=True)
    views_left = Column(Integer, default=0)
    invite_from = Column(GUID(), nullable=True, default=None, index=True)
    payments_history = relationship("PaymentsHistory", back_populates="user")

    def is_subscribe_expire(self) -> bool:
        if self.subscribe_expire is None:
            return True
        tz = pytz.timezone(settings.timezone)

        try:
            return datetime.now(tz) >= tz.localize(self.subscribe_expire)
        except (TypeError, ValueError):
            return datetime.now(tz) >= self.subscribe_expire
