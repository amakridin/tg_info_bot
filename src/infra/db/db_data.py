import json
from typing import Any, Optional

from src.infra.db.db_base import SQLiteBase
from src.infra.db.models import SheetInfo, Bot


class DbDataManager:
    def __init__(self, db_manager: SQLiteBase):
        self._db_manager = db_manager

    async def create_bot(self, bot_name: str, token: str, active: bool) -> None:
        await self._db_manager.crud(
            "INSERT INTO bots(name, token, active) VALUES (:name, :token, :active)",
            dict(name=bot_name, token=token, active=active),
        )

    async def get_bot_info_by_name(self, bot_name: str) -> Optional[Bot]:
        res = await self._db_manager.get(
            "SELECT id, name, token, active, date_created FROM bots WHERE name = :name",
            dict(name=bot_name),
        )
        if res:
            return Bot(**res[0])

    async def get_bot_info_by_token(self, token: str) -> Optional[Bot]:
        res = await self._db_manager.get(
            "SELECT id, name, token, active, date_created FROM bots WHERE token = :token",
            dict(token=token),
        )
        if res:
            return Bot(**res[0])

    async def get_active_bots(self) -> list[dict[str, Any]]:
        return await self._db_manager.get("SELECT * from BOTS where active = true")

    async def _get_bots(self, field: str, value: Any) -> Optional[list[Bot]]:
        query = "SELECT id, name, token, active, date_created from BOTS where {field} = :value".format(
            field=field
        )
        return await self._db_manager.get(query, dict(value=value))

    async def get_sheet_info(self, bot_id: int) -> Optional[SheetInfo]:
        res = await self._db_manager.get(
            "select url, sheet, index_column, columns, extend_columns, date_created from sheets where bot_id = :bot_id",
            dict(bot_id=bot_id),
        )
        if not res:
            return
        sheet_info = res[0]
        sheet_info["columns"] = json.loads(sheet_info["columns"])
        if sheet_info["extend_columns"]:
            sheet_info["extend_columns"] = json.loads(sheet_info["extend_columns"])
        return SheetInfo(**sheet_info)

    async def activate_bot(self, bot_name: str) -> None:
        await self._db_manager.crud(
            "update bots set status = true where name = :name", dict(name=bot_name)
        )

    async def deactivate_bot(self, bot_name: str) -> None:
        await self._db_manager.crud(
            "update bots set status = false where name = :name", dict(name=bot_name)
        )

    async def delete_bot(self, bot_name) -> None:
        bot_info = await self.get_bot_info_by_name(bot_name)
        bot_id = bot_info.id
        await self._db_manager.crud(
            "delete from sheets where bot_id = :bot_id", dict(bot_id=bot_id)
        )
        await self._db_manager.crud(
            "delete from bots where name = :name", dict(name=bot_name)
        )

    async def crud_sheet(
        self,
        bot_name: str,
        sheet_url: str,
        sheet: str,
        index_column: str,
        columns: list[str],
        extend_columns: Optional[list[str]],
    ) -> None:
        bot_info = await self.get_bot_info_by_name(bot_name)
        if not bot_info:
            return
        sheet_info = await self.get_sheet_info(bot_info.id)
        _keys = ["bot_id", "url", "sheet", "index_column", "columns"]
        _values = [":bot_id", ":url", ":sheet", ":index_column", ":columns"]
        _data = dict(
            bot_id=bot_info.id,
            url=sheet_url,
            sheet=sheet,
            index_column=index_column,
            columns=json.dumps(columns),
        )
        if extend_columns:
            _keys.append("extend_columns")
            _values.append(":extend_columns")
            _data["extend_columns"] = json.dumps(extend_columns)

        if sheet_info:
            # do update
            upd_data = [
                f"{_keys[nn + 1]} = {_values[nn + 1]}" for nn in range(len(_keys) - 1)
            ]
            await self._db_manager.crud(
                f"update sheets set {', '.join(upd_data)} where bot_id = :bot_id",
                _data,
            )
        else:
            # do insert
            await self._db_manager.crud(
                f"insert into sheets({', '.join(_keys)}) values({', '.join(_values)})",
                _data,
            )
