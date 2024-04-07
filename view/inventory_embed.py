import discord

from datalayer.inventory import UserInventory
from items.types import ItemType


class InventoryEmbed(discord.Embed):

    def __init__(self, inventory: UserInventory):
        super().__init__(
            title=f"Inventory of {inventory.member_display_name}\nBeans: `🅱️{inventory.balance}`",
            color=discord.Colour.purple(),
            description="All the items you currently own.",
        )
        inventory_items = inventory.items

        if len(inventory_items) == 0:
            self.add_field(name="", value="There is nothing here.", inline=False)

        for item in inventory_items:
            count = inventory.get_item_count(item.type)
            match item.type:
                case ItemType.NAME_COLOR:
                    suffix = ""
                    custom_color = inventory.custom_name_color
                    if custom_color is not None:
                        suffix = f" #{custom_color}"
                    item.add_to_embed(self, 54, count=count, name_suffix=suffix)
                case ItemType.REACTION_SPAM:
                    emoji = inventory.bully_emoji
                    target_name = inventory.bully_target_name
                    if emoji is None or target_name is None:
                        suffix = " - Error, please update settings"
                    else:
                        suffix = f" {target_name} | {str(emoji)}"
                    item.add_to_embed(self, 54, count=count, name_suffix=suffix)
                case _:
                    item.add_to_embed(self, 54, count=count)

        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
