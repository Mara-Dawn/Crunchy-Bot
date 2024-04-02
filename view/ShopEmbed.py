from typing import List
import discord

from CrunchyBot import CrunchyBot
from shop.Item import Item

class ShopEmbed(discord.Embed):
    
    ITEMS_PER_PAGE = 4
    
    def __init__(self, bot: CrunchyBot,  interaction: discord.Interaction, items: List[Item], start_offset:int = 0):
        description = f'Spend your hard earned beans!\n'
        description += f'Only <@{interaction.user.id}> can interact here.\n'
        description += f'Use `/shop` to open your own shop widget.\n'
        description += f'Use `/inventory` or the balance button below to see your inventory. \n'
        super().__init__(
            title=f"Beans Shop for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description=description
        )
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(items))
        items.sort(key=lambda x:x.get_cost())
        display = items[start_offset:end_offset]
        
        for item in display:
            item.add_to_embed(self, 44)
            
        self.set_image(url="attachment://shop.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
