import os
from typing import Union

from yarl import URL


class BaseFileLoader:
    def _validate(self, url: str, host: str) -> bool:
        return URL(url).host == host

    def _check_file_exists(
        self, id: Union[int, str], path: str, bot_id: Union[str, int]
    ) -> str:
        for files in os.walk(f"{path}/{bot_id}/"):
            for file in files[2]:
                if id == file.split(".")[0]:
                    return file
