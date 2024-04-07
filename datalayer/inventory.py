import discord

from items.item import Item
from items.types import ItemType


class UserInventory:

    def __init__(
        self,
        guild_id: int,
        member: int,
        member_display_name: str,
        items: list[Item],
        inventory: dict[ItemType, int],
        balance=int,
        custom_name_color: str = None,
        bully_target_name: str = None,
        bully_emoji: discord.Emoji | str = None,
    ):
        self.guild_id = guild_id
        self.member = member
        self.member_display_name = member_display_name
        self.items = items
        self.inventory = inventory
        self.balance = balance
        self.custom_name_color = custom_name_color
        self.bully_target_name = bully_target_name
        self.bully_emoji = bully_emoji

    def get_item_count(self, item_type: ItemType) -> int:
        if item_type not in self.inventory:
            return 0

        return self.inventory[item_type]
