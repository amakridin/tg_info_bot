from typing import Any, Optional
import aiohttp
from config import GET_UPDATES_TIMEOUT, DEFAULT_HTTP_TIMEOUT
from yarl import URL
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)
BASE_URL = "https://api.telegram.org/bot{tg_token}"


class Attachment(Enum):
    IMAGE = "photo"
    FILE = "document"


class ButtonType(Enum):
    BUTTONS = "inline_keyboard"
    KEYBOARD = "keyboard"
    REQUEST_CONTACT = "request_contact"
    REQUEST_LOCATION = "request_location"
    REQUEST_POOL = "request_poll"


@dataclass
class Buttons:
    buttons: list
    buttons_type: ButtonType


@dataclass
class AttachmentParams:
    file_path: str
    file_type: Attachment


@dataclass
class MessageParams:
    chat_id: int
    message: str
    buttons: list = None
    reply_mid: int = None
    attach: AttachmentParams = None


class KeyboardTypes(Enum):
    CONTACT = "request_contact"
    LOCATION = "request_location"
    POOL = "request_poll"

    @classmethod
    def get_values(cls):
        return cls.POOL.value, cls.CONTACT.value, cls.LOCATION.value

    @classmethod
    def get_type_by_name(cls, name: str):
        if name == cls.CONTACT.value:
            return cls.CONTACT
        elif name == cls.LOCATION.value:
            return cls.LOCATION
        elif name == cls.POOL.value:
            return cls.POOL


@dataclass
class KeyboardParams:
    message: str
    button_text: str
    keyboard_type: KeyboardTypes


@dataclass
class MessageCallbackParams:
    callback_query_id: int
    text: str
    show_alert: bool = False


class TelegramApi:
    def __init__(self, token: str):
        self.url_base = BASE_URL.format(tg_token=token)
        self.longpolling_timeout = GET_UPDATES_TIMEOUT

    async def get_updates(self, offset: int = -1) -> list[Any]:
        method = "getUpdates"
        params = {"timeout": self.longpolling_timeout, "offset": offset}
        url = URL(self.url_base) / method

        try:
            async with aiohttp.request(
                method=aiohttp.hdrs.METH_GET,
                url=url,
                json=params,
                # timeout=aiohttp.ClientTimeout(self.longpolling_timeout + 5),
                # raise_for_status=True
            ) as response:
                res = await response.json()
                return res.get("result", [])
        except Exception as er:
            logger.debug(er)
            return []

    async def send_msg(self, message_params: MessageParams):
        msg_params: dict = dict(chat_id=str(message_params.chat_id))
        method = "sendMessage"
        if message_params.attach:
            msg_params["caption"] = message_params.message
            if message_params.attach.file_type == Attachment.IMAGE:
                method = "sendPhoto"
                if message_params.attach.file_path.startswith("http"):
                    msg_params["photo"] = message_params.attach.file_path
                else:
                    try:
                        with open(message_params.attach.file_path, "rb") as f:
                            msg_params[message_params.attach.file_type.value] = f.read()
                    except Exception as er:
                        logger.info(er)
                        with open("img/no_image.png", "rb") as f:
                            msg_params[message_params.attach.file_type.value] = f.read()
            elif message_params.attach.file_type == Attachment.FILE:
                method = "sendDocument"
                with open(message_params.attach.file_path, "rb") as f:
                    msg_params[message_params.attach.file_type.value] = f.read()
        if message_params.buttons:
            msg_params["reply_markup"] = json.dumps(
                {"inline_keyboard": message_params.buttons}
            )

        if method == "sendMessage":
            msg_params["text"] = message_params.message
            msg_params["parse_mode"] = "HTML"

        url = URL(self.url_base) / method
        try:
            async with aiohttp.request(
                method=aiohttp.hdrs.METH_POST,
                url=url,
                timeout=aiohttp.ClientTimeout(DEFAULT_HTTP_TIMEOUT),
                data=msg_params,
                raise_for_status=False,
            ) as response:
                jsn = await response.json()
                return
        except Exception as er:
            logger.debug(er)

    async def send_keyboard_button(self, chat_id: int, keyboard_params: KeyboardParams = None, remove: bool = False):
        params = {
            "chat_id": chat_id,
            "text": keyboard_params.message,
            "reply_markup": {
                "keyboard": [
                    [
                        {
                            "text": keyboard_params.button_text,
                            keyboard_params.keyboard_type.value: True,
                        }
                    ]
                ],
                "one_time_keyboard": True,
                "resize_keyboard": True,
            },
        } if not remove else {
            "chat_id": chat_id,
            "text": "Спасибо!",
            "reply_markup": {
                "remove_keyboard": True
            }
        }
        method = "sendMessage"
        url = URL(self.url_base) / method

        try:
            async with aiohttp.request(
                    method=aiohttp.hdrs.METH_POST,
                    url=url,
                    json=params,
                    # timeout=aiohttp.ClientTimeout(self.longpolling_timeout + 5),
                    # raise_for_status=True
            )as response:
                jsn = await response.json()
        except Exception as er:
            logger.debug(er)
            return []



    async def send_poll(self, chat_id: int):
        method = "sendPoll"
        with open("img_test.png", "rb") as f:
            file = f.read()
        params = dict(
            chat_id=str(chat_id),
            protect_content=True,
            question="да или нет?",
            options=json.dumps(["да", "нет"]),
            # reply_markup=json.dumps({"inline_keyboard": [[{"text": "Yes"}, {"text": "No"}]]}),
            type="quiz",
            correct_option_id=str(1),
            explanation="потому что нет",
            is_anonymous=str(False),
        )
        url = URL(self.url_base) / method
        async with aiohttp.request(
            method=aiohttp.hdrs.METH_POST,
            url=url,
            timeout=aiohttp.ClientTimeout(DEFAULT_HTTP_TIMEOUT),
            json=params,
            raise_for_status=True,
        ) as response:
            jsn = await response.json()
            return

    async def send_chat_action(self, chat_id: int, message_id: int):
        method = "sendChatAction"
        # typing, upload_photo for photos, record_video or upload_video, record_voice, upload_document for general files, choose_sticker for stickers, find_location for location data, record_video_note or upload_video_note for video notes.
        params = dict(chat_id=chat_id, action="typing")
        url = URL(self.url_base) / method
        async with aiohttp.request(
            method=aiohttp.hdrs.METH_POST,
            url=url,
            timeout=aiohttp.ClientTimeout(DEFAULT_HTTP_TIMEOUT),
            json=params,
            raise_for_status=True,
        ) as response:
            jsn = await response.json()
            return

    async def answer_callback_query(self, params: MessageCallbackParams):
        method = "answerCallbackQuery"
        url = URL(self.url_base) / method
        async with aiohttp.request(
            method=aiohttp.hdrs.METH_POST,
            url=url,
            timeout=aiohttp.ClientTimeout(DEFAULT_HTTP_TIMEOUT),
            json=asdict(params),
            raise_for_status=False,
        ) as response:
            jsn = await response.json()
            return jsn


async def run():
    tg = TelegramApi("5240278243:AAEMmtPTPaqnamswsUBLERaiOjDdYdXc9aA")

    buttons = [
        [
            {"text": "Yes", "callback_data": "btn0"},
            {"text": "No", "callback_data": "btn1"},
        ]
    ]
    # await tg.send_buttons(chat_id=314602198, message="hello", buttons=buttons)

    # await tg.send_msg(MessageParams(chat_id=314602198, message="hello"))
    # await tg.send_msg(MessageParams(chat_id=314602198, message="hello", buttons=buttons))
    # await tg.send_msg(MessageParams(chat_id=314602198, message="hello", buttons=buttons,
    #                                 attach=AttachmentParams(file_path="img_test.png", file_type=Attachment.IMAGE)))
    await tg.send_msg(
        MessageParams(
            chat_id=314602198,
            message="hello",
            buttons=buttons,
            attach=AttachmentParams(
                file_path="img_test.png", file_type=Attachment.FILE
            ),
        )
    )
    # await tg.send_msg(MessageParams(chat_id=314602198, message="hello", buttons=buttons,
    #                                 attach=AttachmentParams(file_path="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg", file_type=Attachment.IMAGE)))
    # await tg.send_poll(chat_id=314602198)
    # await tg.send_quiz(chat_id=314602198)
    # await tg.send_reaction(chat_id=314602198, message_id=478)
    # await tg.answer_callback_query(callback_query_id=1351206155867312113, message="wqewqewqe")


import asyncio

if __name__ == "__main__":
    asyncio.run(run())
