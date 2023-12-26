from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from pydantic import AnyUrl


@dataclass
class EntityModel:
    def dict(self):
        return asdict(self)


@dataclass
class SheetInfo(EntityModel):
    url: AnyUrl
    sheet: str
    index_column: str
    columns: list[str]
    extend_columns: Optional[list[str]]
    date_created: datetime


@dataclass
class Bot(EntityModel):
    id: int
    name: str
    token: str
    active: bool
    date_created: datetime
