import datetime
from typing import Any

from items.types import ItemType

from events.bot_event import BotEvent
from events.types import EventType


class InventoryEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        member_id: int,
        item_type: ItemType,
        amount: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.INVENTORY, id)
        self.member_id = member_id
        self.item_type = item_type
        self.amount = amount

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.item_type, self.amount]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "InventoryEvent":
        from datalayer.database import Database

        if row is None:
            return None
        return InventoryEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            member_id=row[Database.INVENTORY_EVENT_MEMBER_COL],
            item_type=row[Database.INVENTORY_EVENT_ITEM_TYPE_COL],
            amount=row[Database.INVENTORY_EVENT_AMOUNT_COL],
            id=row[Database.EVENT_ID_COL],
        )
