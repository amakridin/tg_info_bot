from typing import Any
from aiohttp import hdrs
from tg_simple_math_bot.settings import Settings
from tg_simple_math_bot.integrations.base import BaseAPI
from yarl import URL

BASE_URL = f"https://api.telegram.org/bot{Settings.TELEGRAM_TOKEN}"


class ApiTelegram(BaseAPI):
    async def get_updates(
        self, offset: int = 0, timeout: int = Settings.GET_UPDATES_TIMEOUT
    ) -> list[Any]:
        method = "getUpdates"
        params = {"timeout": timeout, "offset": offset}
        url = URL(BASE_URL) / method
        try:
            response_body = await self._request(
                url=url, method=hdrs.METH_GET, timeout=timeout, json=params
            )
            return response_body.get("result", [])
        except:
            return []

    async def send_message(self, chat_id: int, message: str, reply_mid: str = None):
        method = "sendMessage"
        params = dict(chat_id=chat_id, text=message, reply_to_msg_id=reply_mid)
        url = URL(BASE_URL) / method
        await self._request(
            url=url,
            method=hdrs.METH_POST,
            timeout=Settings.DEFAULT_TIMEOUT,
            json=params,
        )
