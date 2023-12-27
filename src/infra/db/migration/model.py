from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class BotTable(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    name = Column(String(256), unique=True, nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    date_created = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    description = Column(Text)


Index("ix_bots__token", BotTable.token)


class SheetsTable(Base):
    __tablename__ = "sheets"

    id = Column(Integer, primary_key=True, autoincrement="auto", nullable=False)
    bot_id = Column(
        Integer, ForeignKey("bots.id"), unique=True
    )  # пока разрешаем только 1_old лист для бота
    url = Column(Text, unique=True, nullable=False)
    sheet = Column(Text, nullable=False)
    index_column = Column(Text, nullable=False)
    columns = Column(Text, nullable=False)
    extend_columns = Column(Text, default="[]")
    date_created = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# alembic revision --autogenerate -m "identify db"
# alembic upgrade head
