import logging
from datetime import datetime

logging.basicConfig(filename="bot.log", datefmt="%H:%M:%S", level=logging.ERROR)


class BaseError(Exception):
    message: str = "Unexpected exception"
    status_code: int = 500


class InternalError(BaseError):
    pass


class ServiceNotResponse(BaseError):
    status_code = 500
    message = "Service not response"
    code = "service_not_response"


class WrongRequest(BaseError):
    message = "Wrong request, try \"help\" command"


class DownstreamServiceError(BaseError):
    def __init__(self, url: str, message: str, status_code: int = 400) -> None:
        logging.error(
            f"{datetime.now()} request url: {url}, status_code: {status_code}, message: {message}"
        )

        super().__init__()
