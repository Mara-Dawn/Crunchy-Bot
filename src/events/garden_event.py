import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType, GardenEventType


class GardenEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        garden_id: int,
        plot_id: int,
        member_id: int,
        garden_event_type: GardenEventType,
        payload: str = None,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.GARDEN, id)
        self.garden_id = garden_id
        self.plot_id = plot_id
        self.member_id = member_id
        self.garden_event_type = garden_event_type
        self.payload = payload

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [
            self.garden_id,
            self.plot_id,
            self.garden_event_type,
            self.payload,
        ]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "GardenEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return GardenEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            garden_id=row[Database.GARDEN_EVENT_GARDEN_ID_COL],
            plot_id=row[Database.GARDEN_EVENT_PLOT_ID_COL],
            member_id=row[Database.GARDEN_EVENT_MEMBER_ID],
            garden_event_type=GardenEventType(row[Database.GARDEN_EVENT_TYPE_COL]),
            payload=row[Database.GARDEN_EVENT_PAYLOAD_COL],
            id=row[Database.EVENT_ID_COL],
        )
