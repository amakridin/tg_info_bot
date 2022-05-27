from tg_simple_math_bot.data_types import TgResponse
from typing import Any
from tg_simple_math_bot.services.calculate import Calculate
from tg_simple_math_bot.errors import WrongRequest
from tg_simple_math_bot.services.decorators import log_commands
from tg_simple_math_bot.settings import Settings
import aioredis

redis = aioredis.from_url(Settings.REDIS_DSN, decode_responses=True)


class Handler:
    def __init__(self):
        self.commands = {
            "help": {"descr": "returns all commands", "run": self.command_help},
            "last": {"descr": "returns last commands", "run": self.command_last},
            "total": {"descr": "returns total commands count", "run": self.command_total},
            "clear": {"descr": "clears commands history", "run": self.command_clear},
        }

    async def run(self, tg_response: dict[str:Any]) -> tuple:
        chat_id, command = self.get_command_params(tg_response)
        return await self.get_result(chat_id, command)

    async def get_result(self, chat_id: int, command: str):
        result: str
        if command in self.commands.keys():
            result = await self.commands[command]["run"](chat_id)
        else:
            try:
                calc = Calculate()
                result = await calc(chat_id, command)
            except WrongRequest as ex:
                result = ex.message
        return chat_id, result

    async def command_help(self, *args, **kwargs):
        return "Bot calculates simple math example (+-*/ with using brackets)\nAvailable commands:\n{}".format(
            "\n".join(
                [
                    f"{command} - {command_property.get('descr','')}"
                    for command, command_property in self.commands.items()
                ]
            )
        )

    async def command_last(self, chat_id: int):
        last = await redis.lrange(str(chat_id), 0, Settings.LAST_REQUESTS_COUNT - 1)
        return "last {} commands:\n{}".format(Settings.LAST_REQUESTS_COUNT, "\n".join(last))

    async def command_total(self, chat_id: int):
        total = await redis.llen(str(chat_id))
        return "total commands = {}".format(total)

    async def command_clear(self, chat_id: int):
        await redis.delete(str(chat_id))
        return "done!"

    def get_command_params(self, tg_response: dict[str:Any]):
        parsed_response = TgResponse(**tg_response)
        input_command = parsed_response.message.text.replace(" ", "")
        chat_id = parsed_response.message.chat.id
        return chat_id, input_command
