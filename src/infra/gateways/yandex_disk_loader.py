import os
from typing import Union, Optional

import aiohttp
from urllib.parse import urlencode
from yarl import URL

import logging

from get_config import get_key_config
from src.infra.gateways.base_file_loader import BaseFileLoader

logger = logging.getLogger(__name__)


class YaDiskLoader(BaseFileLoader):
    def __init__(self, bot_id: Union[int, str]):
        self.bot_id = str(bot_id)
        self.base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
        self.host = "disk.yandex.ru"
        self.path = get_key_config("FILE_PATH")

    async def download(self, url: str, overwrite: bool = False) -> Optional[str]:
        """
        :param url:
        :param overwrite:
        :return: downloaded file path
        """
        if not self._validate(url):
            return

        try:
            file_id = URL(url).parts[2].split(".")[0]
            if overwrite or not self._check_file_exists(
                file_id, self.path, self.bot_id
            ):
                async with aiohttp.request(
                    method="GET",
                    url=URL(self.base_url).with_query(urlencode(dict(public_key=url))),
                ) as response:
                    resp_data = await response.json()
                filename = dict(
                    (
                        row.split("=")
                        for row in URL(resp_data["href"]).raw_query_string.split("&")
                    )
                ).get("filename")
                print(f"ya_disk_loader: {url=}, {filename=}")
                filename = f"{file_id}.{filename.split('.')[1]}"
                download_url = resp_data["href"]

                async with aiohttp.request(
                    method="GET", url=download_url
                ) as download_response:
                    with open(f"{self.path}/{self.bot_id}/{filename}", "wb") as f:
                        f.write(await download_response.content.read())
                return f"{self.path}/{self.bot_id}/{filename}"
        except Exception as err:
            logger.error(err)
            return

    def _validate(self, url: str) -> bool:
        return URL(url).host == self.host
