import asyncio
from aio_pika import connect_robust, Message
import asyncio
import aio_pika
import aio_pika.abc
from config import RABBIT_CONNECTION, RABBIT_MESSAGE_TTL


class RabbitMqApi:
    def __init__(self, queue_name: str = None):
        self.queue_name = queue_name
        self.conn_str = RABBIT_CONNECTION

    async def consumer2(self):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                name=self.queue_name, arguments={"x-message-ttl": RABBIT_MESSAGE_TTL}
            )
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        yield message.body

    async def consumer(self):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(name=self.queue_name, arguments={"x-message-ttl": RABBIT_MESSAGE_TTL})

            async for message in queue:
                async with message.process():
                    return message.body

    async def producer(self, message: str):
        connection = await aio_pika.connect(url=self.conn_str)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                name=self.queue_name, arguments={"x-message-ttl": RABBIT_MESSAGE_TTL}
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
