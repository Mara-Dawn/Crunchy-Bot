import datetime

from typing import Any, Dict, List
from events import BotEvent
from events.types import EventType, BeansEventType


class BeansEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        beans_event_type: BeansEventType,
        member: int,
        value: int,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.BEANS, event_id)
        self.beans_event_type = beans_event_type
        self.member = member
        self.value = value

    def get_beans_event_type(self) -> BeansEventType:
        return self.beans_event_type

    def get_member(self) -> int:
        return self.member

    def get_value(self) -> int:
        return self.value

    def get_causing_user_id(self) -> int:
        return self.member

    def get_type_specific_args(self) -> List[Any]:
        return [self.beans_event_type, self.value]

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "BeansEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return BeansEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            beans_event_type=row[Database.BEANS_EVENT_TYPE_COL],
            member=row[Database.BEANS_EVENT_MEMBER_COL],
            value=row[Database.BEANS_EVENT_VALUE_COL],
            event_id=row[Database.EVENT_ID_COL],
        )
