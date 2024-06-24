import datetime
from typing import Any

from items.types import ItemType

from events.bot_event import BotEvent
from events.types import EventType


class InventoryBatchEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        member_id: int,
        items: list[tuple[int, ItemType]],
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.INVENTORYBATCH, id)
        self.member_id = member_id
        self.items = items
        self.amount = len(items)
        self.base_type = EventType.INVENTORY

        self.item_types = [[amount, item][1] for amount, item in items]
        self.amounts = [[amount, item][0] for amount, item in items]

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.items]
