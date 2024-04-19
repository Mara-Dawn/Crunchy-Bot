import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import BeansEventType, EventType


class BeansEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        beans_event_type: BeansEventType,
        member_id: int,
        value: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.BEANS, id)
        self.beans_event_type = beans_event_type
        self.member_id = member_id
        self.value = value

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.beans_event_type, self.value]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "BeansEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return BeansEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            beans_event_type=row[Database.BEANS_EVENT_TYPE_COL],
            member_id=row[Database.BEANS_EVENT_MEMBER_COL],
            value=row[Database.BEANS_EVENT_VALUE_COL],
            id=row[Database.EVENT_ID_COL],
        )
