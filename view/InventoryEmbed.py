from typing import List
import discord

from MaraBot import MaraBot
from datalayer.UserInventory import UserInventory

class InventoryEmbed(discord.Embed):
    
    def __init__(self, bot: MaraBot,  interaction: discord.Interaction, inventory: UserInventory, balance = int):
        super().__init__(
            title=f"Inventory of {interaction.user.display_name}\nBeans: `🅱️{balance}`",
            color=discord.Colour.purple(),
            description=f'All the items you currently own.'
        )
        
        self.item_manager = bot.item_manager
        guild_id = interaction.guild_id
        inventory_items = inventory.get_inventory_items()
        
        if len(inventory_items) == 0:
            self.add_field(name='', value="There is nothing here.", inline=False)
        
        for item_type, count in inventory_items.items():
            item = self.item_manager.get_item(guild_id, item_type)
            item.add_to_embed(self, 61, count=count)
            
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
