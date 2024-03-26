from typing import List
import discord

from MaraBot import MaraBot
from shop.Item import Item

class ShopEmbed(discord.Embed):
    
    def __init__(self, bot: MaraBot,  interaction: discord.Interaction, items: List[Item]):
        super().__init__(
            title=f"Beans Shop for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description='Spend your hard earned beans here!'
        )
        
        for item in items:
            item.add_to_embed(self)
            
        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
