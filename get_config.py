from typing import Union, Any
from dotenv import dotenv_values


def get_key_config(key: str) -> Union[str, int]:
    return _load_config().get(key)


def get_config() -> dict[str, Any]:
    return _load_config()


def _load_config() -> dict:
    return dotenv_values(".env")
