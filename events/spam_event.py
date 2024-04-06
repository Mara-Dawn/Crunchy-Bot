import datetime

from typing import Any, Dict, List
from events import BotEvent
from events.types import EventType


class SpamEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        member: int,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.SPAM, event_id)
        self.member = member

    def get_member(self) -> int:
        return self.member

    def get_causing_user_id(self) -> int:
        return self.member

    def get_type_specific_args(self) -> List[Any]:
        return []

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "SpamEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return SpamEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            member=row[Database.SPAM_EVENT_MEMBER_COL],
            event_id=row[Database.EVENT_ID_COL],
        )
