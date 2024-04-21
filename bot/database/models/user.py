from sqlalchemy import Column, BigInteger

from bot.database.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
