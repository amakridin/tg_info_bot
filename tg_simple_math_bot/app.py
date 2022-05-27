import asyncio
import aioredis
from tg_simple_math_bot.integrations.api_telegram import ApiTelegram
from tg_simple_math_bot.services.handler import Handler
from tg_simple_math_bot.settings import Settings


class SimpleMathBot:
    def __init__(self):
        self.tg_api = ApiTelegram()
        self.handler = Handler()



    async def run(self):
        offset: int = 0
        while True:
            response_data = await self.tg_api.get_updates(offset=offset)
            for response in response_data:
                offset = int(response["update_id"]) + 1
                chat_id, message = await self.handler.run(tg_response=response)
                await self.tg_api.send_message(chat_id=chat_id, message=message)


simple_bot = SimpleMathBot()
asyncio.run(simple_bot.run())
