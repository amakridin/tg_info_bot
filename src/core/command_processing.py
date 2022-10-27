from typing import List

from src.infra.gateways.telegram_api import MessageParams

ADMIN_COMMANDS = {
    "/help": "Общая справка по командам",
    "/ping": "Проверка работает ли бот",
    "/echo": "Возвращает текст, который отправили. \n<i>Пример: /echo привет\nВернет - привет</i>",
    "/send60": "Временное решение. Отправляет пользователям, разеганным в течение последних 60 минут текст, следующий после команды. \n<i>Пример: /send60 Вы зарегались в течение часа</i>",
    "/users": "Выгружает список пользователей",
}


class CommandProcessing:
    def __init__(self):
        pass

    async def __call__(self, message: str) -> List[MessageParams]:
        message = message.strip()
        command, params = message, ""
        if message.find(" ") > 0:
            command = message[0:message.find(" ") + 1].strip()
            params = message[message.find(" ") + 1:].strip()

        if command == "/help":
            msg = []
            for cmnd, descr in ADMIN_COMMANDS.items():
                msg.append(f"<b>{cmnd}</b> - {descr}")
            return [MessageParams(chat_id=0, message="\n".join(msg))]

        elif command == "/ping":
            return [MessageParams(chat_id=0, message="pong")]

        elif command == "/echo":
            if params:
                return [MessageParams(chat_id=0, message=params)]

        elif command == "/send":
            # отправляем всем, кто зарегался за последний час
            pass
