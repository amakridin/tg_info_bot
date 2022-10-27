import asyncio

from config import RABBIT_COMMON_QUEUE
from src.core.command_processing import CommandProcessing, ADMIN_COMMANDS
from src.infra.gateways.rabbitmq_api import RabbitMqApi
from src.infra.gateways.telegram_api import TelegramApi, MessageParams, MessageCallbackParams, KeyboardParams
from src.infra.gateways.redis_api import RedisApi
from src.core.quiz_processing import QuizProcessing, ScoreMessage
from src.core.scenario_processing import ScenarioProcessing, NoBotScenario
from src.infra.db.db_base import SQLiteBase
import json
import logging

logger = logging.getLogger(__name__)


class EventProcessingApp:
    def __init__(self):
        self.bot_list: dict[int, TelegramApi] = dict()
        self.bot_scenario: dict[int, ScenarioProcessing] = dict()
        self.db = SQLiteBase()
        self.rabbit = RabbitMqApi(queue_name=RABBIT_COMMON_QUEUE)
        self.quiz_processing = QuizProcessing()
        self.command_processing = CommandProcessing()

    async def load_token(self, bot_id):
        sql = "select token from bot where active = true and id = :bot_id"
        bot = await self.db.get_one(sql=sql, binds={"bot_id": bot_id})
        if bot:
            self.bot_list[bot_id] = TelegramApi(bot[0])

    async def load_scenario(self, bot_id):
        scenario = ScenarioProcessing(bot_id=bot_id)
        try:
            await scenario.load_scenario()
        except NoBotScenario:
            return
        self.bot_scenario[bot_id] = scenario

    async def handler(self, jsn: dict) -> None:
        bot_id = jsn["bot_id"]
        data = jsn["data"]
        tg_api = self.bot_list.get(bot_id)
        if data.get("message") and data["message"].get("text"):
            # От пользователя пришел текст
            user_id = data["message"]["from"]["id"]
            message = data["message"]["text"]
            chat_id = data["message"]["chat"]["id"]

            if message and message.split(" ")[0] in ADMIN_COMMANDS.keys():
                msgs = await self.command_processing(message)
                for msg in msgs:
                    if isinstance(msg, KeyboardParams):
                        await tg_api.send_keyboard_button(chat_id=chat_id, keyboard_params=msg)
                    else:
                        msg.chat_id = chat_id
                        await tg_api.send_msg(message_params=msg)
            elif message == "/start" or message and not await self.quiz_processing.check_user_session(user_id=user_id):
                # 1/0
                # Начало общения с ботом
                await self.quiz_processing.reboot(user_id)
                if self.bot_scenario.get(bot_id):
                    msgs = await self.bot_scenario[bot_id].step_handle(bot_id=bot_id, user_id=user_id, chat_id=chat_id, message=message)
                    for msg in msgs:
                        if isinstance(msg, KeyboardParams):
                            await tg_api.send_keyboard_button(chat_id=chat_id, keyboard_params=msg)
                        else:
                            await tg_api.send_msg(message_params=msg)


            elif await self.quiz_processing.check_user_session(user_id=user_id):
                #ToDo хорошо бы сделать сообщение что сейчас другая активная сессия и удалять пользовательское сообщение
                pass



        elif data.get("callback_query"):
            # получили нажатие кнопки пользователем
            user_id = data["callback_query"]["from"]["id"]
            callback_data = str(data["callback_query"]["data"])
            chat_id = str(data["callback_query"]["message"]["chat"]["id"])
            if "quiz_start" in callback_data.split(":"):
                # Пользователь запустил викторину
                # перезагружаем бота, забываем активные сессии
                qwiz_name = callback_data.split(":")[-1]
                await self.quiz_processing.reboot(user_id)
                msg_list = await self.quiz_processing.run(user_id=user_id,
                                                          quiz_name=qwiz_name) or []
                for msg in msg_list:
                    if isinstance(msg, MessageParams):
                        msg.chat_id = data["callback_query"]["message"]["chat"]["id"]
                        await tg_api.send_msg(message_params=msg)

            elif "quiz_answer" in callback_data.split(":"):
                # пришел ответ пользователя на вопрос викторины (quiz_answer:1/0), отправляем на обработку
                # если вернется непустое сообщение - отправляем его в чат
                callback_data = callback_data.split(":")[-2:]
                msg_list = await self.quiz_processing.run(user_id=user_id, callback_data=callback_data) or []
                for msg in msg_list:
                    msg.chat_id = chat_id
                    if isinstance(msg, MessageParams):
                        await tg_api.send_msg(message_params=msg)
                    elif isinstance(msg, MessageCallbackParams):
                        msg.callback_query_id = str(data["callback_query"]["id"])
                        await tg_api.answer_callback_query(msg)
                    elif isinstance(msg, ScoreMessage):
                        msgs = await self.bot_scenario[bot_id].step_handle(bot_id=bot_id, user_id=user_id,
                                                                           quiz_result=msg.score,
                                                                           chat_id=chat_id)
                        for msg0 in msgs:
                            msg0.chat_id = data["callback_query"]["message"]["chat"]["id"]
                            if isinstance(msg0, KeyboardParams):
                                await tg_api.send_keyboard_button(chat_id=data["callback_query"]["message"]["chat"]["id"], keyboard_params=msg0)
                            else:
                                await tg_api.send_msg(message_params=msg0)

            else:
                # нажатие кнопки не в квизе
                if self.bot_scenario.get(bot_id):
                    msgs = await self.bot_scenario[bot_id].step_handle(bot_id=bot_id, user_id=user_id, callback=callback_data, chat_id=chat_id)
                    for msg in msgs:
                        if isinstance(msg, KeyboardParams):
                            await tg_api.send_keyboard_button(chat_id=int(chat_id), keyboard_params=msg)
                        else:
                            # msg.chat_id = chat_id
                            await tg_api.send_msg(message_params=msg)

        elif data.get("message", {}).get("contact"):
            # пользователь отправил свой контакт
            phone = data.get("message", {}).get("contact").get("phone_number")
            user_id = data["message"]["from"]["id"]
            chat_id = data["message"]["chat"]["id"]
            await tg_api.send_keyboard_button(chat_id=chat_id, remove=True)

            if self.bot_scenario.get(bot_id):
                msgs = await self.bot_scenario[bot_id].step_handle(bot_id=bot_id, user_id=user_id, message=phone, chat_id=chat_id)
                for msg in msgs:
                    if isinstance(msg, KeyboardParams):
                        await tg_api.send_keyboard_button(chat_id=int(chat_id), keyboard_params=msg)
                    else:
                        msg.chat_id = chat_id
                        await tg_api.send_msg(message_params=msg)


    async def run(self) -> None:
        while True:
            try:
                msg = await self.rabbit.consumer()
                data = json.loads(msg)
                bot_id = data["bot_id"]
                if bot_id not in self.bot_list:
                    await self.load_token(bot_id)
                    await self.load_scenario(bot_id)
                await self.handler(jsn=data)
            except Exception as er:
                logger.debug(er)
