import asyncio
import aioredis

from src.infra.gateways.rabbitmq_api import RabbitMqApi
from src.infra.gateways.telegram_api import TelegramApi
from src.infra.db.db_base import SQLiteBase
from config import RABBIT_COMMON_QUEUE
import json


class EventListenerApp:
    async def listener(self, token: str, bot_id: int):
        offset: int = -1
        tg = TelegramApi(token=token)
        rabbit = RabbitMqApi(queue_name=RABBIT_COMMON_QUEUE)
        while True:
            res = await tg.get_updates(offset=offset)
            for row in res:
                offset = row.get("update_id") + 1
                await rabbit.producer(json.dumps({"bot_id": bot_id, "data": row}))

    async def get_bot_tokens(self) -> dict[int, str]:
        sql = "select id, token from bot where active = true"
        db = SQLiteBase()
        bot_list = await db.get_many(sql=sql)
        if bot_list:
            return dict(bot_list)

    async def run(self):
        while True:
            bot_tokens = await self.get_bot_tokens()
            bot_tokens = bot_tokens or dict()
            tasks = set(
                [
                    int(task.get_name().split(":")[1])
                    for task in asyncio.all_tasks()
                    if task.get_name().startswith("bot")
                ]
            )

            for active_task in bot_tokens.keys() - tasks:
                asyncio.create_task(
                    self.listener(bot_tokens[active_task], active_task), name=f"bot:{active_task}"
                )
            for inactive_task in tasks - bot_tokens.keys():
                for task in asyncio.all_tasks():
                    if task.get_name() == f"bot:{inactive_task}":
                        task.cancel()

            await asyncio.sleep(60)
