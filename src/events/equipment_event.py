import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EquipmentEventType, EventType


class EquipmentEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        member_id: int,
        equipment_event_type: EquipmentEventType,
        item_id: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.EQUIPMENT, id)
        self.member_id = member_id
        self.equipment_event_type = equipment_event_type
        self.item_id = item_id

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.equipment_event_type, self.item_id]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "EquipmentEvent":
        from datalayer.database import Database

        if row is None:
            return None
        return EquipmentEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            member_id=row[Database.EQUIPMENT_EVENT_MEMBER_ID],
            equipment_event_type=row[Database.EQUIPMENT_EVENT_EQUIPMENT_EVENT_TYPE],
            item_id=row[Database.EQUIPMENT_EVENT_ITEM_ID],
            id=row[Database.EVENT_ID_COL],
        )
