from tg_simple_math_bot.settings import Settings
from tg_simple_math_bot.errors import WrongRequest
from tg_simple_math_bot.services.decorators import log_commands

AVAILABLE_SYMBOLS = set("0123456789.*/+-()")


class Calculate:
    @log_commands
    async def __call__(self, chat_id: int, command: str) -> str:
        if self.check_before_calculate(command):
            try:
                return f"{command}={round(eval(command), Settings.MATH_ACCURACY)}"
            except:
                raise WrongRequest
        else:
            raise WrongRequest

    def check_before_calculate(self, input_command: str):
        if len(set(input_command.replace(" ", "")) - AVAILABLE_SYMBOLS) == 0:
            return True
        return False
