from pydantic import BaseModel
from pydantic import PositiveInt
from typing import List


class TgResponseChat(BaseModel):
    id: PositiveInt


class TgResponseMessage(BaseModel):
    message_id: PositiveInt
    text: str
    chat: TgResponseChat


class TgResponse(BaseModel):
    update_id: PositiveInt
    message: TgResponseMessage


class TgResponses(BaseModel):
    response: List[TgResponse]
