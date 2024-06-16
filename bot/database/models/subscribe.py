from sqlalchemy import Column, Integer, CHAR, Boolean, VARCHAR
from sqlalchemy.orm import relationship

from bot.database.models.base import Base


class Subscribe(Base):
    __tablename__ = "subscribes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(VARCHAR(128))
    days = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    visible = Column(Boolean, default=True)
    payments_history = relationship("PaymentsHistory", back_populates="subscribe")
