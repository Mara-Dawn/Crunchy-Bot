import datetime
from typing import Any, Dict

import discord

from events.EventManager import EventManager
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
        cost: int
    ):
        self.name = name
        self.type = type
        self.group = group
        self.description = description
        self.cost = cost
        self.emoji = emoji
     
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
    
    def add_to_embed(self, embed: discord.Embed, count: int=None) -> None:
        max_len = 49
        title = f'> ~*  {self.get_name()}  *~'
        description = self.get_description()
        
        if count is None:
            suffix = f'🅱️{self.get_cost()}'
        else:
            suffix = f'owned: {count}'
        spacing = max_len - len(suffix)
        info_block = f'```{description}\n\n{' '*spacing}{suffix}```'
        
        embed.add_field(name=title, value=info_block, inline=False)
    
    def activated():
        pass
        
    def use(self, event_manager: EventManager, guild_id: int, member_id: int):
        pass