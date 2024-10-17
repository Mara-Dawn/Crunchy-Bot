import discord
from discord.ext import commands

from config import Config
from datalayer.inventory import UserInventory
from items.item import Item
from items.types import ItemState, ItemType


class InventoryEmbed(discord.Embed):

    ITEMS_PER_PAGE = 5

    def __init__(
        self,
        bot: commands.Bot,
        inventory: UserInventory,
        display_items: list[Item] = None,
    ):
        super().__init__(
            title=f"Inventory of {inventory.member_display_name}\nBeans: `🅱️{inventory.balance}`",
            color=discord.Colour.purple(),
            description="All the items you currently own.",
        )
        author_name = bot.user.display_name
        author_img = bot.user.display_avatar
        self.set_author(name=author_name, icon_url=author_img)

        if display_items is None:
            display_items = []

        if len(display_items) == 0:
            self.add_field(name="", value="There is nothing here.", inline=False)
            return

        for item in display_items:
            count = inventory.get_item_count(item.type)
            disabled = inventory.get_item_state(item.type) is ItemState.DISABLED
            match item.type:
                case ItemType.NAME_COLOR:
                    suffix = ""
                    custom_color = inventory.custom_name_color
                    if custom_color is not None:
                        suffix = f" #{custom_color}"
                    item.add_to_embed(
                        bot,
                        self,
                        Config.INVENTORY_ITEM_MAX_WIDTH,
                        count=count,
                        name_suffix=suffix,
                        disabled=disabled,
                    )
                case ItemType.REACTION_SPAM:
                    emoji = inventory.bully_emoji
                    target_name = inventory.bully_target_name
                    if emoji is None or target_name is None:
                        suffix = " - Error, please update settings"
                    else:
                        suffix = f" {target_name} | {str(emoji)}"
                    item.add_to_embed(
                        bot,
                        self,
                        Config.INVENTORY_ITEM_MAX_WIDTH,
                        count=count,
                        name_suffix=suffix,
                        disabled=disabled,
                    )
                case _:
                    item.add_to_embed(
                        bot,
                        self,
                        Config.INVENTORY_ITEM_MAX_WIDTH,
                        count=count,
                        disabled=disabled,
                    )
