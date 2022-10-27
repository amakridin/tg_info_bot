import aiosqlite
from config import ASYNC_DB_CONNECTION
from typing import Optional, Any, Union


class CRUDOperationError(Exception):
    pass


class SQLiteBase:
    def __init__(self, conn_str: str = None):
        self.conn_str = conn_str or ASYNC_DB_CONNECTION

    async def crud(self, sql: str, binds: Optional[dict[str, Any]] = None) -> None:
        async with aiosqlite.connect(self.conn_str) as db:
            try:
                # await db.execute("PRAGMA journal_mode=WAL")
                await db.execute(sql, binds)
                await db.commit()
            except Exception as ex:
                await db.rollback()
                raise CRUDOperationError from ex

    async def get_one(self, sql: str, binds: Optional[dict[str, Any]] = None) -> Union[tuple[Any], None]:
        async with aiosqlite.connect(self.conn_str) as db:
            async with db.execute(sql, binds) as cursor:
                return await cursor.fetchone()

    async def get_many(self, sql: str, binds: Optional[dict[str, Any]] = None) -> Union[list[tuple[Any]], None]:
        async with aiosqlite.connect(self.conn_str) as db:
            async with db.execute(sql, binds) as cursor:
                res = await cursor.fetchall()
                if len(res) > 0:
                    return res


async def run():
    db = SQLiteBase("botssss.db")
    # await db.crud("insert into user(date_created, rel_bot, user_id) values (CURRENT_TIMESTAMP, 1, 3)")
    # await db.crud("delete from user")
    # await db.crud("update scenario set db_target='user.add_info' where id=4")
    # await db.crud("update scenario set buttons='[[\n  {\"text\": \"IT\", \"callback\": \"it\"},\n  {\"text\": \"Бухгалтер\", \"callback\": \"buh\"}\n]]' where id=4")
    # await db.crud("insert into scenario(rel_bot, step, next_step, text) values (3, 110, null, 'Спасибо. Вернуться в начало /start')")
    res = await db.get_many("select * from user")
    # res = await db.get_many("select * from scenario")
    res = res or ()
    for row in res:
        print(row)


import asyncio

if __name__ == "__main__":
    asyncio.run(run())
