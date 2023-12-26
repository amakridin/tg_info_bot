import aio_pika
import aio_pika.abc
from aio_pika import Message

from get_config import get_key_config


class RabbitMqApi:
    def __init__(self, queue_name: str = None):
        self.queue_name = queue_name
        self.conn_str = get_key_config("RABBIT_CONNECTION")
        self.ttl = int(get_key_config("RABBIT_MESSAGE_TTL"))

    async def consume2(self):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                name=self.queue_name, arguments={"x-message-ttl": self.ttl}
            )
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        yield message.body

    async def consume(self):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                name=self.queue_name, arguments={"x-message-ttl": self.ttl}
            )

            async for message in queue:
                async with message.process():
                    return message.body

    async def produce(self, message: str):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                name=self.queue_name, arguments={"x-message-ttl": self.ttl}
            )
            await channel.default_exchange.publish(
                Message(message.encode()), routing_key=queue.name
            )


# from config import RABBIT_COMMON_QUEUE
# async def run():
#     r = RabbitMqApi(RABBIT_COMMON_QUEUE)
#     # await r.producer("hello world")
#     # await r.producer("как дела?")
#     async for msg in r.consumer():
#         print(msg)
#
#
# if __name__ == "__main__":
#     asyncio.run(run())
