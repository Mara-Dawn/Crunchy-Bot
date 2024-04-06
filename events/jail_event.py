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
        caused_by: int,
        duration: int,
        jail_reference: int,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.JAIL, event_id)
        self.jail_event_type = jail_event_type
        self.caused_by = caused_by
        self.duration = duration
        self.jail_reference = jail_reference

    def get_jail_event_type(self) -> JailEventType:
        return self.jail_event_type

    def get_caused_by(self) -> int:
        return self.caused_by

    def get_duration(self) -> int:
        return self.duration

    def get_jail_id(self) -> int:
        return self.jail_reference

    def get_causing_user_id(self) -> int:
        return self.caused_by

    def get_type_specific_args(self) -> list[Any]:
        return [self.jail_event_type, self.duration, self.jail_reference]

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
            caused_by=row[Database.JAIL_EVENT_BY_COL],
            duration=row[Database.JAIL_EVENT_DURATION_COL],
            jail_reference=row[Database.JAIL_EVENT_JAILREFERENCE_COL],
            event_id=row[Database.EVENT_ID_COL],
        )
