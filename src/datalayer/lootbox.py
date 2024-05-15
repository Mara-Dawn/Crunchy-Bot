from typing import Any  # noqa: UP035

from items.types import ItemType


class LootBox:

    SPECIAL_ITEMS = [
        ItemType.CHEST_BEANS,
        ItemType.CHEST_LARGE_MIMIC,
        ItemType.CHEST_MIMIC,
        ItemType.CHEST_SPOOK_MIMIC,
    ]

    MIMICS = [
        ItemType.CHEST_LARGE_MIMIC,
        ItemType.CHEST_MIMIC,
        ItemType.CHEST_SPOOK_MIMIC,
    ]
    SMALL_MIN_BEANS = 30
    SMALL_MAX_BEANS = 80
    LARGE_MIN_BEANS = 500
    LARGE_MAX_BEANS = 800

    def __init__(
        self,
        guild_id: int,
        items: dict[ItemType, int],
        beans: int = 0,
        message_id: int = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.message_id = message_id
        self.items = items
        self.beans = beans  # deprecated
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
