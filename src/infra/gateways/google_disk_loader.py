from typing import Union, Optional

import aiohttp

from requests import Response
from yarl import URL

import logging

from get_config import get_key_config
from src.infra.gateways.base_file_loader import BaseFileLoader

logger = logging.getLogger(__name__)


class GoogleDiskLoader(BaseFileLoader):
    def __init__(self, bot_id: Union[int, str]):
        self.bot_id = bot_id
        self.base_url = "https://docs.google.com/uc"
        self.host = "drive.google.com"
        self.path = get_key_config("FILE_PATH")

    async def download(self, url: str, overwrite: bool = False) -> Optional[str]:
        if not self._validate(url, self.host):
            return
        try:
            file_id = URL(url).parts[3]
            if overwrite or not self._check_file_exists(
                file_id, self.path, self.bot_id
            ):
                async with aiohttp.request(
                    method="GET",
                    url=URL(self.base_url),
                    params=dict(export="download", confirm=1, id=file_id),
                ) as response:
                    filename = (
                        dict(
                            [
                                [elem.strip() for elem in row.split("=")]
                                for row in response.headers.get(
                                    "Content-Disposition"
                                ).split(";")
                                if len(row.split("=")) == 2
                            ]
                        )
                        .get("filename")
                        .replace('"', "")
                    )
                    print(f"google_disk_loader: {url=}, {filename=}")
                    filename = f"{file_id}.{filename.split('.')[1]}"
                    with open(f"{self.path}/{self.bot_id}/{filename}", "wb") as f:
                        f.write(await response.content.read())

            return f"{self.path}/{self.bot_id}/{filename}"
        except Exception as err:
            logger.error(err)
            return

    def _get_confirm_token(self, response: Response):
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value


# async def run():
#     goo = GoogleDiskLoader(bot_id=111)
#     await goo.download(url="https://drive.google.com/file/d/1YMMXEFkL5XQyYRFSWnoOoePEzKHbknGs/view?usp=sharing")
#
# asyncio.run(run())
