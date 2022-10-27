from typing import List

from src.infra.db.db_base import SQLiteBase
from src.infra.gateways.telegram_api import MessageParams, TelegramApi

ADMIN_COMMANDS = {
    "/help": "Общая справка по командам",
    "/ping": "Проверка работает ли бот",
    "/echo": "Возвращает текст, который отправили. \n<i>Пример: /echo привет\nВернет - привет</i>",
    "/send60": "Временное решение. Отправляет пользователям, разеганным в течение последних 60 минут текст, следующий после команды. \n<i>Пример: /send60 Вы зарегались в течение часа</i>",
    "/users": "Выгружает список пользователей",
}


class CommandProcessing:
    def __init__(self):
        self.db = SQLiteBase()

    async def __call__(self, bot_id: int, message: str) -> List[MessageParams]:
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

        elif command == "/send60":
            # отправляем всем, кто зарегался за последний час
            if params:
                token = await self.get_bot_token(bot_id)
                sql = "select chat_id from user where chat_id is not NULL and datetime(date_created)>=datetime('now', '-1 Hour');"
                result = await self.db.get_many(sql=sql)
                if result:
                    tg = TelegramApi(token=token)
                    for row in result:
                        await tg.send_msg(MessageParams(chat_id=row[0], message=params))

    async def get_bot_token(self, bot_id: int) -> str:
        token = await self.db.get_one(sql="select token from bot where id=:id", binds={"id": bot_id})
        return token[0]
