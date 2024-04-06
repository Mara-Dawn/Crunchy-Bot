from typing import Any, Dict
from items.types import ItemType


class LootBox:

    def __init__(
        self,
        guild_id: int,
        item_type: ItemType,
        beans: int,
        message_id: int = None,
        lootbox_id: int = None,
    ):
        self.guild_id = guild_id
        self.message_id = message_id
        self.item_type = item_type
        self.beans = beans
        self.lootbox_id = lootbox_id

    def get_guild_id(self) -> int:
        return self.guild_id

    def set_message_id(self, message_id: int) -> None:
        self.message_id = message_id

    def get_message_id(self) -> int:
        return self.message_id

    def get_item_type(self) -> ItemType:
        return self.item_type

    def get_beans(self) -> str:
        return self.beans

    def get_id(self) -> int:
        return self.lootbox_id

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> "LootBox":
        from datalayer.atabase import Database

        if row is None:
            return None

        return LootBox(
            guild_id=int(row[Database.LOOTBOX_GUILD_COL]),
            message_id=int(row[Database.LOOTBOX_MESSAGE_ID_COL]),
            item_type=row[Database.LOOTBOX_ITEM_TYPE_COL],
            beans=int(row[Database.LOOTBOX_BEANS_COL]),
            lootbox_id=int(row[Database.LOOTBOX_ID_COL]),
        )
