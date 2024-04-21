from sqlalchemy import Column, BigInteger, String

from bot.database.models.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, unique=True, autoincrement=True)
    movie_id = Column(String(length=128))
    file_id = Column(String(length=64), nullable=True)
    
