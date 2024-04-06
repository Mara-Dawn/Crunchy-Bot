import datetime

from typing import Any, Dict, List
from events import BotEvent
from events.types import EventType


class BatEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        used_by_id: int,
        target_id: int,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.BAT, event_id)
        self.used_by_id = used_by_id
        self.target_id = target_id

    def get_used_by_id(self) -> int:
        return self.used_by_id

    def get_target_id(self) -> int:
        return self.target_id

    def get_causing_user_id(self) -> int:
        return self.used_by_id

    def get_type_specific_args(self) -> List[Any]:
        return [self.target_id]

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "BatEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return BatEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            used_by_id=row[Database.BAT_EVENT_USED_BY_COL],
            target_id=row[Database.BAT_EVENT_TARGET_COL],
            event_id=row[Database.EVENT_ID_COL],
        )
