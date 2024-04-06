import discord
from datalayer.inventory import UserInventory
from items.types import ItemType


class InventoryEmbed(discord.Embed):

    def __init__(self, inventory: UserInventory):
        super().__init__(
            title=f"Inventory of {inventory.get_display_name()}\nBeans: `🅱️{inventory.get_balance()}`",
            color=discord.Colour.purple(),
            description="All the items you currently own.",
        )

        inventory_items_counts = inventory.get_inventory_items_counts()

        if len(inventory_items_counts) == 0:
            self.add_field(name="", value="There is nothing here.", inline=False)

        for item in inventory.get_items():
            count = inventory.get_item_count(item.get_type())
            match item.get_type():
                case ItemType.NAME_COLOR:
                    suffix = ""
                    custom_color = inventory.get_custom_name_color()
                    if custom_color is not None:
                        suffix = f" #{custom_color}"
                    item.add_to_embed(self, 54, count=count, name_suffix=suffix)
                case ItemType.REACTION_SPAM:
                    emoji = inventory.get_bully_emoji()
                    target_name = inventory.get_bully_target_name()
                    if emoji is None or target_name is None:
                        suffix = " - Error, please update settings"
                    else:
                        suffix = f" {target_name} | {str(emoji)}"
                    item.add_to_embed(self, 54, count=count, name_suffix=suffix)
                case _:
                    item.add_to_embed(self, 54, count=count)

        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
