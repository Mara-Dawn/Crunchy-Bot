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
        
        max_len = 49
        for item in items:
            title = f'> ~*  {item.get_name()}  *~'
            description = item.get_description()
            cost = f'🅱️{item.get_cost()}'
            spacing = max_len - len(cost)
            info_block = f'```{description}\n\n{' '*spacing}{cost}```'
            
            self.add_field(name=title, value=info_block, inline=False)
            
        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
