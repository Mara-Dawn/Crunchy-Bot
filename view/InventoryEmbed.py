from typing import List
import discord

from MaraBot import MaraBot
from datalayer.UserInventory import UserInventory

class InventoryEmbed(discord.Embed):
    
    def __init__(self, bot: MaraBot,  interaction: discord.Interaction, inventory: UserInventory):
        super().__init__(
            title=f"Inventory of {interaction.user.display_name}",
            color=discord.Colour.purple(),
            description='All the items you currently own.'
        )
        
        self.item_manager = bot.item_manager
        guild_id = interaction.guild_id
        inventory_items = inventory.get_inventory_items()
        
        if len(inventory_items) == 0:
            self.add_field(name='', value="There is nothing here.", inline=False)
        
        max_len = 49
        for item_type, count in inventory_items.items():
            
            item = self.item_manager.get_item(guild_id, item_type)
            
            title = f'> ~*  {item.get_name()}  *~'
            description = item.get_description()
            owned = f'owned: {count}'
            spacing = max_len - len(owned)
            info_block = f'```{description}\n\n{' '*spacing}{owned}```'
            
            self.add_field(name=title, value=info_block, inline=False)
            
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
