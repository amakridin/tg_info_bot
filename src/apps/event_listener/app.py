import asyncio
import json
from dataclasses import asdict

from get_config import get_key_config
from src.core.models import BotEvent
from src.infra.db.db_base import SQLiteBase
from src.infra.db.db_data import DbDataManager
from src.infra.gateways.rabbitmq_api import RabbitMqApi
from src.infra.gateways.telegram_api import TelegramApi


class EventListenerApp:
    def __init__(self):
        self.rabbit_common_queue = get_key_config("RABBIT_COMMON_QUEUE")

    async def listen(self, token: str, bot_id: int):
        offset: int = -1
        tg = TelegramApi(token=token)
        rabbit = RabbitMqApi(queue_name=self.rabbit_common_queue)
        while True:
            res = await tg.get_updates(offset=offset)
            for row in res:
                offset = row.get("update_id") + 1
                event = BotEvent(
                    bot_id=bot_id,
                    chat_id=row.get("message").get("chat").get("id"),
                    token=token,
                    payload=row,
                )
                await rabbit.produce(json.dumps(asdict(event)))

    async def __call__(self, *args, **kwargs):
        db = DbDataManager(SQLiteBase())
        while True:
            bots = await db.get_active_bots() or []
            tasks = set(
                [
                    int(task.get_name().split(":")[1])
                    for task in asyncio.all_tasks()
                    if task.get_name().startswith("bot")
                ]
            )
            for bot in bots:
                if bot["id"] not in tasks:
                    await asyncio.create_task(
                        self.listen(bot["token"], bot["id"]),
                        name="bot:{bot_id}".format(bot_id=bot["id"]),
                    )

            # for inactive_task in tasks - bot_tokens.keys():
            #     for task in asyncio.all_tasks():
            #         if task.get_name() == f"bot:{inactive_task}":
            #             task.cancel()

            await asyncio.sleep(60)
