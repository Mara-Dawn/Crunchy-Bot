import datetime
from typing import Any, Dict, List

import discord

from datalayer.UserInteraction import UserInteraction
from events.EventManager import EventManager
from shop.Item import Item
from shop.ItemGroup import ItemGroup
from shop.ItemType import ItemType

class InstantItem(Item):

    def __init__(
        self,
        name: str, 
        type: ItemType,
        group: ItemGroup,
        description: str,
        emoji: str,
        cost: int,
        view_class: str,
        value: Any,
        embed: discord.Embed = None,
        allow_amount: bool = False,
        base_amount: int = 1
    ):
        self.name = name
        self.description = description
        self.embed = embed
        self.view_class = view_class
        self.value = value
        self.allow_amount = allow_amount
        super().__init__(name, type, group, description, emoji, cost, base_amount)

    def get_embed(self) -> discord.Embed:
        title = f'{self.get_emoji()} {self.get_name()}'
        description = self.get_description()
        max_width = 60
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        suffix = f'🅱️{self.get_cost()}'
        spacing = max_width - len(suffix)
        info_block = f'```{description}\n\n{' '*spacing}{suffix}```'
        
        embed = discord.Embed(title=title, description=info_block, color=discord.Colour.purple()) if self.embed is None else self.embed
        
        return embed
    
    def get_value(self) -> Any:
        return self.value
    
    def get_view_class(self) -> str:
        return self.view_class
    
    def get_allow_amount(self) -> bool:
        return self.allow_amount
        
            