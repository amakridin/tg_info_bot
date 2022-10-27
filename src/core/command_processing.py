from typing import List

from src.infra.db.db_base import SQLiteBase
from src.infra.gateways.telegram_api import MessageParams, TelegramApi

ADMIN_COMMANDS = {
    "/help": "Общая справка по командам",
    "/ping": "Проверка работает ли бот",
    "/echo": "Возвращает текст, который отправили. \n<i>Пример: /echo привет\nВернет - привет</i>",
    "/send60": "Временное решение. Отправляет пользователям, разеганным в течение последних 60 минут текст, следующий после команды. \n<i>Пример: /send60 Вы зарегались в течение часа</i>",
    "/users": "Выгружает список пользователей",
    "/delusers": "Удаляет пользователей",
    "/user/count": "Выгружает количество пользователей",
    "/myid": "возвращает мой id",
    "/admin/add": "добавляем админа. Пример: /admin/add 123455 где 123456 - это user_id (получаем по команде /myid",
    "/admin/remove": "Удаляем админа. Пример: /admin/add 123455 где 123456 - это user_id",
    "/admin/list": "список id админов",
}

COMMON_COMMANDS = ["/myid", "/ping", "/echo"]


class CommandProcessing:
    def __init__(self):
        self.db = SQLiteBase()

    async def __call__(self, bot_id: int, user_id: int, message: str) -> List[MessageParams]:
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
            msg = []
            if params:
                sql = "select chat_id from user where rel_bot=:bot_id and datetime(date_created)>=datetime('now', '-1 Hour');"
                result = await self.db.get_many(sql=sql, binds={"bot_id": bot_id})
                cnt = len(result) if result else 0
                if result:
                    for row in result:
                        msg.append(MessageParams(chat_id=int(row[0]), message=params))
            msg.append(MessageParams(chat_id=0, message=f"отправлено сообщений: {cnt}"))
            return msg

        elif command == "/delusers":
            sql = "delete from user"
            await self.db.crud(sql=sql)

        elif command == "/user/count":
            # возвращаем кол-во пользователей
            if params:
                sql = "select count(1) from user where rel_bot=:bot_id"
                result = await self.db.get_one(sql=sql, binds={"bot_id": bot_id})
                return [MessageParams(chat_id=0, message=f"Кол-во пользователей: {result[0]}")]

        elif command == "/myid":
            return [MessageParams(chat_id=0, message=f"Мой id: {user_id}")]

        elif command == "/admin/add":
            sql = "insert into admin(user_id) select :user_id where not exists(select 0 from admin where user_id=:user_id)"
            await self.db.crud(sql, {"user_id": user_id})
            return [MessageParams(chat_id=0, message=f"Ok")]

        elif command == "/admin/remove":
            sql = "delete from admin where user_id=:user_id"
            await self.db.crud(sql, {"user_id": user_id})
            return [MessageParams(chat_id=0, message=f"Ok")]

        elif command == "/admin/list":
            sql = "select user_id from admin order by user_id"
            result = await self.db.get_many(sql)
            res = []
            for row in result:
                res.append(row[0])
            return [MessageParams(chat_id=0, message="id админов: {}".format(", ".join(res)))]


    async def get_bot_token(self, bot_id: int) -> str:
        token = await self.db.get_one(sql="select token from bot where id=:id", binds={"id": bot_id})
        return token[0]
