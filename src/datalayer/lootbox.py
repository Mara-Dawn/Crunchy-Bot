from typing import Any  # noqa: UP035

from items.types import ItemType


class LootBox:

    def __init__(
        self,
        guild_id: int,
        items: dict[ItemType, int],
        beans: int,
        message_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.message_id = message_id
        self.items = items
        self.beans = beans
        self.id = id

    @staticmethod
    def from_db_row(row: dict[str, Any], items: dict[ItemType, int]) -> "LootBox":
        from datalayer.database import Database

        if row is None:
            return None

        return LootBox(
            guild_id=int(row[Database.LOOTBOX_GUILD_COL]),
            message_id=int(row[Database.LOOTBOX_MESSAGE_ID_COL]),
            items=items,
            beans=int(row[Database.LOOTBOX_BEANS_COL]),
            id=int(row[Database.LOOTBOX_ID_COL]),
        )
