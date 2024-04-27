from typing import Any  # noqa: UP035

from items.types import ItemType


class LootBox:

    def __init__(
        self,
        guild_id: int,
        item_type: ItemType,
        beans: int,
        message_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.message_id = message_id
        self.item_type = item_type
        self.beans = beans
        self.id = id

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "LootBox":
        from datalayer.database import Database

        if row is None:
            return None

        return LootBox(
            guild_id=int(row[Database.LOOTBOX_GUILD_COL]),
            message_id=int(row[Database.LOOTBOX_MESSAGE_ID_COL]),
            item_type=ItemType(row[Database.LOOTBOX_ITEM_TYPE_COL]),
            beans=int(row[Database.LOOTBOX_BEANS_COL]),
            id=int(row[Database.LOOTBOX_ID_COL]),
        )
