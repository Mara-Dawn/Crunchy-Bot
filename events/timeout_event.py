import datetime

from typing import Any, Dict, List
from events import BotEvent
from events.types import EventType


class TimeoutEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        member: int,
        duration: int,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.TIMEOUT, event_id)
        self.member = member
        self.duration = duration

    def get_member(self) -> int:
        return self.member

    def get_duration(self) -> int:
        return self.duration

    def get_causing_user_id(self) -> int:
        return self.member

    def get_type_specific_args(self) -> List[Any]:
        return [self.duration]

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "TimeoutEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return TimeoutEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            member=row[Database.TIMEOUT_EVENT_MEMBER_COL],
            duration=row[Database.TIMEOUT_EVENT_DURATION_COL],
            event_id=row[Database.EVENT_ID_COL],
        )
