import asyncio
import json

from src.core.command_processing import CommandProcessing
from src.core.models import BotEvent
from src.infra.gateways.rabbitmq_api import RabbitMqApi


class EventProcessingQueue:
    def __init__(
        self,
        processing: CommandProcessing,
        rabbitmq_api: RabbitMqApi,
        max_size: int = 5,
    ):
        self.max_size = max_size
        self.processing = processing
        self.rabbitmq_api = rabbitmq_api
        self.queue = asyncio.Queue(maxsize=max_size)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.queue.join()

    async def run(self):
        await asyncio.gather(
            self._produce(), *[self._consume() for _ in range(self.max_size)]
        )

    async def _produce(self) -> None:
        while True:
            task = await self.rabbitmq_api.consume()
            await self.queue.put(BotEvent(**json.loads(task)))

    async def _consume(self) -> None:
        while True:
            task = await self.queue.get()
            await self.processing(task)
            self.queue.task_done()
