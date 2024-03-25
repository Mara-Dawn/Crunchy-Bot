import datetime

from typing import Any, Dict
from events.BotEvent import BotEvent
from events.EventType import EventType
from shop.ItemType import ItemType

class InventoryEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member_id: int,
        item_type: ItemType,
        beans_event_id: int,
        amount: int,
        event_id: int = None
    ):
        super().__init__(timestamp, guild_id, EventType.INVENTORY, event_id)
        self.member_id = member_id
        self.item_type = item_type
        self.beans_event_id = beans_event_id
        self.amount = amount

    def get_member_id(self) -> int:
        return self.member_id
     
    def get_item_type(self) -> ItemType:
        return self.item_type

    def get_beans_event_id(self) -> int:
        return self.beans_event_id
    
    def get_amount(self) -> int:
        return self.amount
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'InventoryEvent':
        from datalayer.Database import Database
        if row is None:
            return None
        return InventoryEvent(
            timestamp = datetime.datetime.fromtimestamp(row[Database.EVENT_TIMESTAMP_COL]),
            guild_id = row[Database.EVENT_GUILD_ID_COL],
            member_id = row[Database.INVENTORY_EVENT_MEMBER_COL],
            item_type = row[Database.INVENTORY_EVENT_ITEM_TYPE_COL],
            beans_event_id = row[Database.INVENTORY_EVENT_BEANS_EVENT_COL],
            amount = row[Database.INVENTORY_EVENT_AMOUNT],
            event_id = row[Database.EVENT_ID_COL]
        )