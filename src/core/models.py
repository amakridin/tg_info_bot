from dataclasses import dataclass
from typing import Callable, Optional

from pydantic import AnyUrl


@dataclass
class BotEvent:
    bot_id: int
    chat_id: int
    token: str
    payload: dict


@dataclass
class CommandParams:
    command: str
    description: str
    handler: Callable


@dataclass
class HandlerParams:
    bot_id: Optional[int] = None
    command: Optional[str] = None


@dataclass
class HandledMessageResponse:
    message: Optional[str] = None
    image_url: Optional[str] = None
