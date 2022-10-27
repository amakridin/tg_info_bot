import json
from typing import List, Optional, Union

from config import REDIS_SCENARIO_DB
from src.infra.db.db_base import SQLiteBase
from src.infra.gateways.redis_api import RedisApi
from src.infra.gateways.telegram_api import (
    MessageParams,
    MessageCallbackParams,
    KeyboardParams,
    KeyboardTypes,
)


class NoBotScenario(Exception):
    pass


class ScenarioProcessing:
    def __init__(self, bot_id: int) -> None:
        self.bot_id = bot_id
        self.redis = RedisApi(db=REDIS_SCENARIO_DB)
        self.db = SQLiteBase()
        self.scenario: dict[int, dict] = dict()

    async def load_scenario(self) -> None:
        sql = "select step, next_step, text, buttons, db_target, sleep from scenario where rel_bot=:bot_id order by 1"
        datas = await self.db.get_many(sql=sql, binds={"bot_id": self.bot_id})
        if not datas:
            raise NoBotScenario
        for data in datas:
            btns = json.loads(data[3]) if data[3] else None
            btns_next_step = {}
            keyboard = []
            if btns:
                for btn in btns:
                    for nn, row in enumerate(btn):
                        if not row.get("keyboard_button_type"):
                            btn[nn] = {
                                "text": row["text"],
                                "callback_data": f'{data[0]}:{row.get("callback")}',
                            }
                            btns_next_step[row["callback"]] = row.get("next_step")
                        else:
                            if row.get("keyboard_button_type") in KeyboardTypes.get_values():
                                keyboard.append(
                                    KeyboardParams(
                                        message=data[2],
                                        keyboard_type=KeyboardTypes.get_type_by_name(
                                            row.get("keyboard_button_type")
                                        ),
                                        button_text=row.get("text"),
                                    )
                                )

            self.scenario[data[0]] = {
                "next_step": data[1],
                "text": data[2],
                "buttons": btns,
                "keyboard": keyboard if len(keyboard) > 0 else None,
                "btns_next_step": btns_next_step,
                "db_target": data[4],
                "sleep": data[5],
            }

    async def step_handle(
        self,
        bot_id: int,
        user_id: int,
        chat_id: int,
        message: str = None,
        callback: str = None,
        quiz_result: int = None
    ) -> Optional[List[MessageParams]]:

        if message == "/start":
            return await self._get_start_messages(user_id, bot_id, chat_id) or []
        elif callback:
            return await self._get_callback_messages(user_id, bot_id, callback, chat_id) or []
        elif message:
            return await self._get_text_messages(user_id, bot_id, message, chat_id) or []
        elif quiz_result:
            return (
                await self._get_quiz_result_messages(user_id, bot_id, quiz_result, chat_id) or []
            )

    async def _get_start_messages(
        self, user_id: int, bot_id: int, chat_id: int
    ) -> Union[List[MessageParams], None]:
        step = 1
        messages = []
        try:
            await self.db.crud(
                sql=f"insert into user(date_created, rel_bot, user_id, chat_id) select CURRENT_TIMESTAMP, :bot_id, :user_id, :chat_id where not exists (select 1 from user where user_id=:user_id)",
                binds={"bot_id": bot_id, "user_id": user_id, "chat_id": chat_id},
            )
            await self.db.crud(
                sql=f"update user set chat_id=:chat_id where user_id=:user_id and bot_id=:bot_id",
                binds={"bot_id": bot_id, "user_id": user_id, "chat_id": chat_id},
            )
        except:
            pass
        await self.redis.set(key=f"{bot_id}:{user_id}", value=step)
        scenario_step = self.scenario.get(step)
        if scenario_step["buttons"]:
            messages.append(
                MessageParams(
                    chat_id=chat_id,
                    message=scenario_step["text"],
                    buttons=scenario_step["buttons"],
                )
            )
        else:
            messages.append(MessageParams(chat_id=chat_id, message=scenario_step["text"]))
        return messages

    async def _get_text_messages(
        self, user_id: int, bot_id: int, message: str, chat_id: int
    ) -> Union[List[MessageParams], None]:
        step = await self.redis.get(key=f"{bot_id}:{user_id}")
        if step:
            step = int(step)
        else:
            return
        messages = []

        scenario_step = self.scenario.get(step)
        if scenario_step.get("db_target"):
            table_name, field_name = scenario_step.get("db_target").split(".")
            await self.db.crud(
                sql=f"update {table_name} set {field_name} = :message where user_id = :user_id",
                binds={"message": message, "user_id": user_id},
            )
        next_step = scenario_step["next_step"]
        if next_step:
            await self.redis.set(key=f"{bot_id}:{user_id}", value=next_step)
            scenario_step = self.scenario.get(next_step)
            if scenario_step["buttons"]:
                messages.append(
                    MessageParams(
                        chat_id=chat_id,
                        message=scenario_step["text"],
                        buttons=scenario_step["buttons"],
                    )
                )
            else:
                messages.append(MessageParams(chat_id=chat_id, message=scenario_step["text"]))

            if scenario_step["keyboard"]:
                messages.extend(scenario_step["keyboard"])

            return messages

    async def _get_callback_messages(
        self, user_id: int, bot_id: int, callback: str, chat_id: int,
    ) -> Union[List[MessageParams], None]:
        step = await self.redis.get(key=f"{bot_id}:{user_id}")
        if step:
            step = int(step)
        else:
            return

        callback_step, callback = callback.split(":")[0:2]
        if step != int(callback_step):
            return

        messages = []

        scenario_step = self.scenario.get(step)
        if scenario_step.get("db_target"):
            table_name, field_name = scenario_step.get("db_target").split(".")
            await self.db.crud(
                sql=f"update {table_name} set {field_name} = :message where user_id = :user_id",
                binds={"message": callback, "user_id": user_id},
            )
        next_step = (
            scenario_step["btns_next_step"][callback]
            if scenario_step["btns_next_step"].get(callback)
            else scenario_step["next_step"]
        )

        if next_step:
            await self.redis.set(key=f"{bot_id}:{user_id}", value=next_step)
            scenario_step = self.scenario.get(next_step)
            if scenario_step["buttons"]:
                messages.append(
                    MessageParams(
                        chat_id=chat_id,
                        message=scenario_step["text"],
                        buttons=scenario_step["buttons"],
                    )
                )
            else:
                messages.append(MessageParams(chat_id=chat_id, message=scenario_step["text"]))
            return messages

    async def _get_quiz_result_messages(
        self, user_id: int, bot_id: int, score: int, chat_id: int
    ) -> Union[List[MessageParams], None]:
        step = await self.redis.get(key=f"{bot_id}:{user_id}")
        if step:
            step = int(step)
        else:
            return

        messages = []

        scenario_step = self.scenario.get(step)
        if scenario_step.get("db_target"):
            table_name, field_name = scenario_step.get("db_target").split(".")
            await self.db.crud(
                sql=f"update {table_name} set {field_name} = :score where user_id = :user_id",
                binds={"score": score, "user_id": user_id},
            )
        next_step: str = None
        for key, val in scenario_step["btns_next_step"].items():
            if str(key).startswith("quiz_start"):
                next_step = val
                break
        next_step = next_step or scenario_step["next_step"]

        if next_step:
            await self.redis.set(key=f"{bot_id}:{user_id}", value=next_step)
            scenario_step = self.scenario.get(next_step)
            if scenario_step["buttons"]:
                messages.append(
                    MessageParams(
                        chat_id=chat_id,
                        message=scenario_step["text"],
                        buttons=scenario_step["buttons"],
                    )
                )
            else:
                messages.append(MessageParams(chat_id=chat_id, message=scenario_step["text"]))
            return messages
