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

    def get_guild_id(self) -> int:
        return self.guild_id

    def get_member_id(self) -> int:
        return self.member

    def get_display_name(self) -> str:
        return self.member_display_name

    def get_items(self) -> list[Item]:
        return self.items

    def get_item_count(self, item_type: ItemType) -> int:
        if item_type not in self.inventory:
            return 0

        return self.inventory[item_type]

    def get_balance(self) -> int:
        return self.balance

    def get_custom_name_color(self) -> str:
        return self.custom_name_color

    def get_bully_target_name(self) -> str:
        return self.bully_target_name

    def get_bully_emoji(self) -> discord.Emoji | str:
        return self.bully_emoji
