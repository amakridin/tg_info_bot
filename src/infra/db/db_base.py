import enum
import json
from dataclasses import dataclass
from typing import Any, Optional, Union

import aiosqlite

from get_config import get_key_config
from src.infra.db.exceptions import EntityNotFound, CRUDOperationError


class BotFilters(str, enum.Enum):
    name = "name"
    token = "token"
    active = "active"


class Operator(str, enum.Enum):
    EQ = "="
    NOT_EQ = "!="
    IN = "IN"
    NOT_IN = "NOT IN"


class Operation(str, enum.Enum):
    AND = "AND"
    OR = "OR"


@dataclass
class Condition:
    filter: str
    operator: Operator
    value: Any


@dataclass
class Conditions:
    operation: Operation
    conditions: list[Union[Condition, "Conditions"]]


cond = Conditions(
    operation=Operation.OR,
    conditions=[
        Conditions(
            operation=Operation.AND,
            conditions=[
                Condition(filter="name", operator=Operator.EQ, value="name1"),
                Condition(filter="status", operator=Operator.EQ, value=True),
            ],
        ),
        Conditions(
            operation=Operation.AND,
            conditions=[
                Condition(filter="name", operator=Operator.EQ, value="name2"),
                Condition(filter="status", operator=Operator.EQ, value=False),
            ],
        ),
        Condition(filter="id", operator=Operator.EQ, value=1),
    ],
)
"""
name="name1" and status=true or 
name="name2" and status=false or 
id=1_old
"""

lvls = ["lvl1_a", ["lvl2_a", "lvl2_b", ["lvl3_a"]], ["lvl2_c", ["lvl3_b"]]]

from collections.abc import Iterable


def unwrap_list(lvls: list):
    res = []
    for lvl in lvls:
        if isinstance(lvl, Iterable) and not isinstance(lvl, str):
            res += unwrap_list(lvl)
        else:
            res.append(lvl)
    return res


print(unwrap_list(lvls))


class SQLiteBase:
    def __init__(self, conn_str: str = None):
        self.conn_str = conn_str or get_key_config("ASYNC_DB_CONNECTION")

    async def crud(self, sql: str, binds: Optional[dict[str, Any]] = None) -> None:
        async with aiosqlite.connect(self.conn_str) as db:
            try:
                await db.execute(sql, binds)
                await db.commit()
            except Exception as ex:
                await db.rollback()
                raise CRUDOperationError from ex

    async def get(
        self, sql: str, binds: Optional[dict[str, Any]] = None
    ) -> Optional[list[dict]]:
        async with aiosqlite.connect(self.conn_str) as db:
            async with db.execute(sql, binds) as cursor:
                names_list = list(
                    [description[0] for description in cursor.description]
                )
                res = await cursor.fetchall()
                if len(res) > 0:
                    return [
                        dict([(names_list[nn], elem) for nn, elem in enumerate(row)])
                        for row in res
                    ]
                else:
                    raise EntityNotFound


async def run():
    db = SQLiteBase("goods.db")
    # await db.crud("delete from bots;")
    # await db.crud("insert into bots(name, token, active) values ('test_AX2023bot', '6625849610:AAHxP3DUuskdWXIlwsJosDTSWvWu7SOhYGo', true)")
    # print(await db.get("select * from bots"))
    await db.crud("delete from sheets;")
    await db.crud(
        "insert into sheets(bot_id, url, sheet, index_column, columns) values(:bot_id, :url, :sheet, :index_column, :columns)",
        dict(
            bot_id=1,
            url="https://docs.google.com/spreadsheets/d/1RXct_j8nxPjH-tmuw8tzN8b3KkFQGLp5yZxOD_ArZGg/edit#gid=0",
            sheet="Лист1",
            index_column="Номер для бота",
            columns=json.dumps(
                ["Автор", "Изделие", "Материал", "Описание", "Ссылка на фото"]
            ),
        ),
    )
    sheets = await db.get("select * from sheets")
    # sheet = sheets[0]
    # print(json.loads(sheet["columns"]))


import asyncio

if __name__ == "__main__":
    asyncio.run(run())
