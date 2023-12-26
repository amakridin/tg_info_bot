import asyncio

from get_config import get_key_config
from src.apps.event_processing.app import EventProcessingQueue
from src.core.command_processing import CommandProcessing
from src.infra.gateways.rabbitmq_api import RabbitMqApi

event_processing = EventProcessingQueue(
    max_size=3,
    processing=CommandProcessing(),
    rabbitmq_api=RabbitMqApi(queue_name=get_key_config("RABBIT_COMMON_QUEUE")),
)

asyncio.run(event_processing.run())
