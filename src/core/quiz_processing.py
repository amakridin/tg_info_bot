import json
import random
from typing import Union
from uuid import uuid4
from config import REDIS_QUIZ_DB
from src.infra.gateways.redis_api import RedisApi
from src.infra.gateways.telegram_api import (
    MessageParams,
    AttachmentParams, Attachment,
    MessageCallbackParams,
)
from dataclasses import dataclass


@dataclass
class ScoreMessage:
    score: int


class QuizProcessing:
    def __init__(self):
        self.redis = RedisApi(db=REDIS_QUIZ_DB)

    async def prepare_quiz(self, user_id: int, quiz_name: str):
        with open(f"scenario/{quiz_name}.json") as f:
            jsn = json.load(f)

        questions = jsn.get("questions")
        first_question_id = None
        for question in questions:
            q_id = str(uuid4())
            if not first_question_id:
                first_question_id = q_id
            question["id"] = q_id
        if jsn.get("shuffle"):
            random.shuffle(questions)
        jsn["questions"] = questions
        jsn["question_count"] = len(questions)
        jsn["question_index"] = 0
        jsn["question_id"] = first_question_id
        jsn["score"] = 0
        await self.redis.delete(user_id)
        await self.redis.set(key=user_id, value=json.dumps(jsn))

    async def build_question(self, question: dict):
        message = question.get("question").get("text")
        img = question.get("question").get("img")
        id = question.get("id")
        right_answer = question.get("answers").get("right_answer")
        hint = question.get("answers").get("hint")
        btns = question.get("answers").get("list")
        nn = 0
        for lst in btns:
            for n, sub in enumerate(lst):
                lst[n] = {"text": sub, "callback_data": "quiz_answer:{}:{}".format(id, int(nn == right_answer))}
                nn += 1
        if hint:
            btns.append([{"text": "подсказка", "callback_data": f"quiz_answer:{id}:hint"}])
        if img:
            return MessageParams(chat_id=0, message=message, buttons=btns, attach=AttachmentParams(file_path=img, file_type=Attachment.IMAGE))
        else:
            return MessageParams(chat_id=0, message=message, buttons=btns)

    async def build_answer(self, explanation: str, is_correct: bool):
        if is_correct:
            return MessageCallbackParams(callback_query_id=0, text="Верно!")
        else:
            return MessageCallbackParams(
                callback_query_id=0, text=explanation, show_alert=True
            )

    async def build_hint(self, hint: str):
        return MessageCallbackParams(callback_query_id=0, text=hint, show_alert=True)

    async def summing(self, quiz: dict) -> MessageParams:
        score = quiz["score"]
        question_count = quiz["question_count"]
        score_range = quiz["score_range"]
        for start, stop, result in score_range:
            if start <= score <= stop:
                return MessageParams(chat_id=0, message=f"{score} из {question_count}.\n {result}")

    async def run(
        self, user_id: int, quiz_name: str = None, callback_data: list = None
    ) -> list[Union[MessageParams, MessageCallbackParams]]:
        message_list = []
        if quiz_name:
            await self.prepare_quiz(user_id, quiz_name)
        quiz_str = await self.redis.get(key=user_id)
        if quiz_str is None:
            return

        quiz: dict = json.loads(quiz_str)
        actual_question_id = quiz["question_id"]
        if callback_data:
            question_id, callback_data = callback_data
            if question_id != actual_question_id:
                return []

        question_ix = quiz["question_index"]
        question_count = quiz["question_count"]

        # Если пользователь берет подсказку
        if callback_data == "hint":
            hint = quiz["questions"][question_ix].get("answers").get("hint")
            msg = await self.build_hint(hint)
            message_list.append(msg)
            # Ничего больше не делаем - отдаем подсказку
            return message_list

        # Если это ответ пользователя на вопрос
        if callback_data is not None and callback_data in ("0", "1"):
            is_correct = bool(int(callback_data))
            if is_correct:
                quiz["score"] = quiz["score"] + 1
            explanation = quiz["questions"][question_ix].get("answers").get("explanation")
            question_ix = question_ix + 1
            quiz["question_index"] = question_ix

            if quiz["check_answer"]:
                msg = await self.build_answer(
                    explanation=explanation, is_correct=is_correct
                )
                message_list.append(msg)

        # Если это был последний вопрос, подводим итоги
        if question_ix == question_count:

            result = await self.summing(quiz)
            await self.redis.delete(user_id)
            message_list.append(result)
            message_list.append(ScoreMessage(score=quiz["score"]))
        # Иначе, продолжаем опрос
        else:
            quiz["question_id"] = quiz["questions"][question_ix].get("id")
            await self.redis.set(key=user_id, value=json.dumps(quiz))
            ask_question = quiz["questions"][question_ix]
            # ToDo в ключ добавить id бота, есть вероятность что один и тот же пользователь будет активен в 2х квизах (user_id:bot_id:chat_id)
            msg = await self.build_question(ask_question)
            message_list.append(msg)

        return message_list

    async def reboot(self, user_id: int) -> None:
        await self.redis.delete(key=user_id)

    async def check_user_session(self, user_id: int) -> bool:
        quiz_data = await self.redis.get(key=user_id)
        if quiz_data:
            return True
        return False
