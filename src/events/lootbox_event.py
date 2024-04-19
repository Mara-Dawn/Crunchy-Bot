import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType, LootBoxEventType


class LootBoxEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        lootbox_id: int,
        member_id: int,
        loot_box_event_type: LootBoxEventType,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.LOOTBOX, id)
        self.lootbox_id = lootbox_id
        self.member_id = member_id
        self.loot_box_event_type = loot_box_event_type

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.lootbox_id, self.loot_box_event_type]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "LootBoxEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return LootBoxEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            lootbox_id=row[Database.LOOTBOX_EVENT_LOOTBOX_ID_COL],
            member_id=row[Database.LOOTBOX_EVENT_MEMBER_COL],
            loot_box_event_type=row[Database.LOOTBOX_EVENT_TYPE_COL],
            id=row[Database.EVENT_ID_COL],
        )
