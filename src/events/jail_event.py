import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType, JailEventType


class JailEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        jail_event_type: JailEventType,
        caused_by_id: int,
        duration: int,
        jail_id: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.JAIL, id)
        self.jail_event_type = jail_event_type
        self.caused_by_id = caused_by_id
        self.duration = duration
        self.jail_id = jail_id

    def get_causing_user_id(self) -> int:
        return self.caused_by_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.jail_event_type, self.duration, self.jail_id]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "JailEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return JailEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            jail_event_type=row[Database.JAIL_EVENT_TYPE_COL],
            caused_by_id=row[Database.JAIL_EVENT_BY_COL],
            duration=row[Database.JAIL_EVENT_DURATION_COL],
            jail_id=row[Database.JAIL_EVENT_JAILREFERENCE_COL],
            id=row[Database.EVENT_ID_COL],
        )
