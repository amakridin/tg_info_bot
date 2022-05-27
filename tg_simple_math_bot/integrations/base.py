import asyncio
from typing import Any, Optional, Union, cast
import json
import aiohttp
from aiohttp import ClientResponse
from aiohttp.typedefs import StrOrURL
from tg_simple_math_bot.errors import (
    DownstreamServiceError,
    ServiceNotResponse,
    InternalError,
)


class BaseAPI:
    async def _request(
        self,
        method: str,
        url: StrOrURL,
        timeout: Optional[int],
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any
    ) -> Union[dict[str, Any], list[Any]]:
        headers = headers or {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    timeout=timeout,
                    headers=headers,
                    ssl=False,
                    **kwargs
                ) as response:
                    resp_json_body = await response.json()
                    await self._check_error(response)
                    return cast(dict[str, object], resp_json_body)

        except aiohttp.client_exceptions.ContentTypeError as ex:
            DownstreamServiceError(url=response.url, message=ex)
            raise ServiceNotResponse
        except aiohttp.ClientError as ex:
            DownstreamServiceError(url=response.url, message=ex)
            raise InternalError
        except asyncio.exceptions.TimeoutError as ex:
            DownstreamServiceError(url=response.url, message=ex)
            raise InternalError

    async def _check_error(self, response: ClientResponse):
        response_status = response.status
        if response_status < 200:
            return
        if response_status >= 400:
            error_message = await response.text()
            DownstreamServiceError(
                url=response.url, message=error_message, status_code=response_status
            )
