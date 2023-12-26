import os
from typing import Callable, Optional

import logging

import validators
from yarl import URL

from get_config import get_key_config
from src.core.models import (
    BotEvent,
    CommandParams,
    HandlerParams,
    HandledMessageResponse,
)
from src.infra.db.db_base import SQLiteBase
from src.infra.db.db_data import DbDataManager
from src.infra.gateways.google_disk_loader import GoogleDiskLoader
from src.infra.gateways.google_sheets_api import GoogleSheetsApi
from src.infra.gateways.redis_api import RedisApi
from src.infra.gateways.telegram_api import (
    Attachment,
    AttachmentParams,
    MessageParams,
    TelegramApi,
)
from src.infra.gateways.yandex_disk_loader import YaDiskLoader

logger = logging.getLogger(__name__)


class CommandProcessing:
    def __init__(self):
        self.db_data_manager = DbDataManager(SQLiteBase())
        self.redis = RedisApi()
        self.admin_command_token = get_key_config("ADMIN_COMMAND_TOKEN")
        self.google_sheets_api = GoogleSheetsApi()

        self.admin_commands = [
            CommandParams(
                command="/help",
                handler=self.handle_help_command,
                description="Общая справка по командам",
            ),
            CommandParams(
                command="/refresh",
                handler=self.handle_refresh_command,
                description="Перечитать Google Sheets",
            ),
            CommandParams(
                command="/refresh_all",
                handler=self.handle_refresh_all_command,
                description="Перечитать Google Sheets",
            ),
            CommandParams(
                command="/sql",
                handler=self.handle_sql_command,
                description="выполняет sql запрос",
            ),
        ]

        self.common_commands = [
            CommandParams(
                command="/start",
                handler=self.handle_start_command,
                description="Тут описание бота",
            ),
        ]

    async def __call__(self, event: BotEvent):
        try:
            payload = event.payload
            message: str = (payload.get("message") or {}).get("text")
            command, *command_tail = message.split(" ")

            if command.startswith("/"):
                response = (
                    await self.process_admin_command(
                        bot_id=event.bot_id, message=message
                    )
                    or await self.process_common_command(
                        bot_id=event.bot_id, message=message
                    )
                    or HandledMessageResponse(message="Команда не распознана")
                )
            elif not command_tail:
                response = await self.process_text_command(
                    bot_id=event.bot_id, message=message
                )
            else:
                response = HandledMessageResponse(message="Команда не распознана.")

            tg_api = TelegramApi(token=event.token)
            await tg_api.send_msg(
                MessageParams(
                    chat_id=event.chat_id,
                    message=response.message,
                    attach=AttachmentParams(
                        file_path=response.image_url, file_type=Attachment.IMAGE
                    )
                    if response.image_url
                    else None,
                )
            )
        except Exception as err:
            logger.error(err)

    async def process_admin_command(
        self, bot_id: int, message: str
    ) -> Optional[HandledMessageResponse]:
        try:
            admin_command, admin_command_token, *tail = message.split()
        except:
            return
        handler = self.get_command_handler(admin_command, self.admin_commands)
        if not handler:
            return
        if admin_command_token != self.admin_command_token:
            return HandledMessageResponse(message="Неверный токен")
        return HandledMessageResponse(
            message=await handler(
                HandlerParams(bot_id=bot_id, command=" ".join(tail) if tail else None)
            )
        )

    async def process_common_command(
        self, bot_id: int, message: str
    ) -> Optional[HandledMessageResponse]:
        try:
            admin_command, *tail = message.split()
        except:
            return
        handler = self.get_command_handler(admin_command, self.common_commands)
        if not handler:
            return
        return HandledMessageResponse(message=await handler())

    async def process_text_command(
        self,
        bot_id: int,
        message: str,
    ) -> HandledMessageResponse:
        return HandledMessageResponse(
            message=await self.redis.hash_map_get_item(bot_id, message)
            or "Команда не распознана",
            image_url=await self.redis.hash_map_get_item(f"img_{bot_id}", message),
        )

    def get_command_handler(
        self, command: str, command_list: list[CommandParams]
    ) -> Optional[Callable]:
        for command_params in command_list:
            if command == command_params.command:
                return command_params.handler

    async def handle_help_command(self, handler_params: HandlerParams) -> str:
        result = []
        result.append("<b>Команды администратора</b> (/команда токен уточнение):")
        for command_params in self.admin_commands:
            result.append(
                f"<b>{command_params.command}</b> - {command_params.description}"
            )

        result.append("<b>Общие команды</b> (/команда уточнение):")
        for command_params in self.common_commands:
            result.append(
                f"<b>{command_params.command}</b> - {command_params.description}"
            )
        return "\n".join(result)

    async def handle_refresh_command(self, handler_params: HandlerParams) -> str:
        return await self._refresh_cache(handler_params, refresh_files=False)

    async def handle_refresh_all_command(self, handler_params: HandlerParams) -> str:
        return await self._refresh_cache(handler_params, refresh_files=True)

    async def _refresh_cache(
        self, handler_params: HandlerParams, refresh_files: bool
    ) -> str:
        ya_disk_loader = YaDiskLoader(bot_id=handler_params.bot_id)
        google_disk_loader = GoogleDiskLoader(bot_id=handler_params.bot_id)

        sheet_info = await self.db_data_manager.get_sheet_info(handler_params.bot_id)
        data = self.google_sheets_api.get_data_by_sheet_url(
            sheet_info.url, sheet_info.sheet
        )
        await self.redis.delete(handler_params.bot_id)
        if refresh_files:
            await self.redis.delete(f"img_{handler_params.bot_id}")
        for row in data:
            row_data = []
            ix_data = str(row.get(sheet_info.index_column))
            if (
                not ix_data
                or handler_params.command
                and handler_params.command != ix_data
            ):
                continue
            for column in sheet_info.columns:
                if row.get(column):
                    if validators.url(row.get(column).split()[0]):
                        url = URL(row.get(column).split()[0])

                        file_path = await ya_disk_loader.download(url, refresh_files)
                        if not file_path:
                            file_path = await google_disk_loader.download(
                                url, refresh_files
                            )
                        if file_path:
                            await self.redis.hash_map_set_key(
                                f"img_{handler_params.bot_id}",
                                ix_data,
                                file_path,
                            )
                    else:
                        row_data.append(f"<b>{column}</b>")
                        row_data.append(str(row.get(column)))
                        row_data.append("")
            if ix_data is not None:
                await self.redis.hash_map_set_key(
                    handler_params.bot_id, ix_data, "\n".join(row_data)
                )
        return "Обновление выполнено"

    async def handle_sql_command(self, token: str, sql: str) -> str:
        return "в разработке"

    async def handle_start_command(self) -> str:
        return "Описание бота"
