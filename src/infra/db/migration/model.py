import enum

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class BotTable(Base):
    __tablename__ = "bot"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    name = Column(String(256), unique=True, nullable=True)
    token = Column(String(256), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date_updated = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


Index("ix_bot__token", BotTable.token)


class UserTable(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    rel_bot = Column(Integer, ForeignKey("bot.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(100))
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    occupation = Column(String(100))
    personal_data_agree = Column(String(5))
    score = Column(Integer)
    add_info = Column(String(250))
    chat_id = Column(Integer)
    date_created = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


Index("ix_user__rel_bot", UserTable.rel_bot)


class ScenarioTable(Base):
    __tablename__ = "scenario"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    rel_bot = Column(Integer, ForeignKey("bot.id"), nullable=False)
    step = Column(Integer, nullable=False)
    next_step = Column(Integer)
    text = Column(Text)
    text_answer_validation = Column(String(50))
    buttons = Column(Text)
    db_target = Column(String(70))
    action = Column(String(50))
    sleep = Column(Integer)


Index("ix_scenario__rel_bot", ScenarioTable.rel_bot)
Index("ix_scenario__id__rel_bot", ScenarioTable.rel_bot, ScenarioTable.step)


class AdminTable(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    user_id = Column(Integer)

# alembic revision --autogenerate -m "identify db"
# alembic upgrade head
