import discord

from typing import Any, Dict
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class Item():

    def __init__(
        self,
        name: str, 
        type: ItemType,
        group: ItemGroup,
        description: str,
        emoji: str,
        cost: int,
        base_amount: int = 1
    ):
        self.name = name
        self.type = type
        self.group = group
        self.description = description
        self.cost = cost
        self.emoji = emoji
        self.base_amount = base_amount
     
    def get_name(self) -> str:
        return self.name
    
    def get_type(self) -> ItemType:
        return self.type
    
    def get_group(self) -> ItemGroup:
        return self.group
    
    def get_description(self) -> str:
        return self.description
    
    def get_emoji(self) -> str:
        return self.emoji
    
    def get_cost(self) -> int:
        return self.cost
    
    def get_base_amount(self) -> int:
        return self.base_amount
    
    def add_to_embed(self, embed: discord.Embed, max_width: int, count: int=None) -> None:
        title = f'> ~*  {self.get_emoji()} {self.get_name()} {self.get_emoji()}  *~'
        description = self.get_description()
        
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        if count is None:
            suffix = f'🅱️{self.get_cost()}'
        else:
            suffix = f'owned: {count}'
        spacing = max_width - len(suffix)
        info_block = f'```{description}\n\n{' '*spacing}{suffix}```'
        
        embed.add_field(name=title, value=info_block, inline=False)
    
    def activated():
        pass
        
    def use():
        pass