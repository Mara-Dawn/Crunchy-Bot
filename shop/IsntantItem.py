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
        view_class: discord.ui.View,
        embed: discord.Embed = None,
        base_amount: int = 1
    ):
        self.name = name
        self.description = description
        self.embed = embed
        self.view_class = view_class
        super().__init__(name, type, group, description, emoji, cost, base_amount)

    def get_embed(self):
        embed = discord.Embed(title=self.name, description=self.description, color=discord.Colour.purple()) if self.embed is None else self.embed
        return embed
    
    def get_view_class(self):
        return self.view_class
        
            