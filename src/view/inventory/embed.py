import discord
from datalayer.inventory import UserInventory
from items.types import ItemState, ItemType


class InventoryEmbed(discord.Embed):

    ITEMS_PER_PAGE = 10

    def __init__(
        self,
        inventory: UserInventory,
        start_offset: int = 0,
    ):
        super().__init__(
            title=f"Inventory of {inventory.member_display_name}\nBeans: `🅱️{inventory.balance}`",
            color=discord.Colour.purple(),
            description="All the items you currently own.",
        )
        inventory_items = inventory.items

        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
        if len(inventory_items) == 0:
            self.add_field(name="", value="There is nothing here.", inline=False)
            return

        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(inventory_items))
        display = inventory_items[start_offset:end_offset]

        for item in display:
            count = inventory.get_item_count(item.type)
            disabled = inventory.get_item_state(item.type) is ItemState.DISABLED
            match item.type:
                case ItemType.NAME_COLOR:
                    suffix = ""
                    custom_color = inventory.custom_name_color
                    if custom_color is not None:
                        suffix = f" #{custom_color}"
                    item.add_to_embed(
                        self, 56, count=count, name_suffix=suffix, disabled=disabled
                    )
                case ItemType.REACTION_SPAM:
                    emoji = inventory.bully_emoji
                    target_name = inventory.bully_target_name
                    if emoji is None or target_name is None:
                        suffix = " - Error, please update settings"
                    else:
                        suffix = f" {target_name} | {str(emoji)}"
                    item.add_to_embed(
                        self, 56, count=count, name_suffix=suffix, disabled=disabled
                    )
                case _:
                    item.add_to_embed(self, 56, count=count, disabled=disabled)
