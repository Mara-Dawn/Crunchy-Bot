from typing import List
import discord

from MaraBot import MaraBot
from shop.Item import Item

class ShopEmbed(discord.Embed):
    
    ITEMS_PER_PAGE = 4
    
    def __init__(self, bot: MaraBot,  interaction: discord.Interaction, items: List[Item], start_offset:int = 0):
        super().__init__(
            title=f"Beans Shop for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description=f'Spend your hard earned beans! \n Only <@{interaction.user.id}> can interact here, use /shop to open your own shop widget.'
        )
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(items))
        items.sort(key=lambda x:x.get_cost())
        display = items[start_offset:end_offset]
        
        for item in display:
            self.add_field(name='', value='', inline=False)
            item.add_to_embed(self, 49)
            
        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
