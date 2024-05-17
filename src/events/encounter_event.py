import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EncounterEventType, EventType


class EncounterEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        encounter_id: int,
        member_id: int,
        encounter_event_type: EncounterEventType,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.ENCOUNTER, id)
        self.encounter_id = encounter_id
        self.member_id = member_id
        self.encounter_event_type = encounter_event_type
        self.id = id

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [
            self.encounter_id,
            self.encounter_event_type,
        ]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "EncounterEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return EncounterEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            encounter_id=row[Database.ENCOUNTER_EVENT_ENCOUNTER_ID_COL],
            member_id=row[Database.ENCOUNTER_EVENT_MEMBER_ID],
            encounter_event_type=EncounterEventType(
                row[Database.ENCOUNTER_EVENT_TYPE_COL]
            ),
            id=row[Database.EVENT_ID_COL],
        )
