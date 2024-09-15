from sqlalchemy import Column, BigInteger, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from bot.database.models.base import Base, SLBigInteger


class PaymentsHistory(Base):
    __tablename__ = "payments_history"

    id = Column(SLBigInteger, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    subscribe_id = Column(Integer, ForeignKey("subscribes.id"))
    subscribe = relationship("Subscribe", back_populates="payments_history")
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="payments_history")
    extra_data = Column(JSONB)
