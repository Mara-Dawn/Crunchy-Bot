import datetime
import discord

from typing import Any, Dict, List
from RoleManager import RoleManager
from datalayer.ItemTrigger import ItemTrigger
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
        cost: int,
        value: int,
        view_class: str = None,
        allow_amount: bool = False,
        base_amount: int = 1,
        max_amount: int = None,
        trigger: List[ItemTrigger] = None
    ):
        self.name = name
        self.type = type
        self.group = group
        self.description = description
        self.cost = cost
        self.value = value
        self.emoji = emoji
        self.view_class = view_class
        self.allow_amount = allow_amount
        self.base_amount = base_amount
        self.max_amount = max_amount
        self.trigger = trigger
     
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
    
    def get_value(self) -> Any:
        return self.value
    
    def get_allow_amount(self) -> bool:
        return self.allow_amount
    
    def get_base_amount(self) -> int:
        return self.base_amount
    
    def get_max_amount(self) -> int:
        return self.max_amount
    
    def get_view_class(self) -> str:
        return self.view_class
    
    def activated(self, action: ItemTrigger):
        if self.trigger is None:
            return False
        return action in self.trigger
    
    def get_embed(self, color=discord.Colour.purple(), amount_in_cart: int = 1) -> discord.Embed:
        title = f'{self.get_emoji()} {self.get_name()}'
        description = self.get_description()
        max_width = 60
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        suffix = f'🅱️{self.get_cost()*amount_in_cart}'
        spacing = max_width - len(suffix)
        info_block = f'```{description}\n\n{' '*spacing}{suffix}```'
        
        embed = discord.Embed(title=title, description=info_block, color=color)
        
        return embed
    
    def add_to_embed(self, embed: discord.Embed, max_width: int, count: int=None, name_suffix: str='') -> None:
        title = f'> ~*  {self.get_emoji()} {self.get_name()} {self.get_emoji()}  *~ {name_suffix}'
        description = self.get_description()
        
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        if count is None:
            suffix = f'🅱️{self.get_cost()}'
        else:
            suffix = f'amount: {count}'
        spacing = max_width - len(suffix)
        info_block = f'```{description}\n\n{' '*spacing}{suffix}```'
        
        embed.add_field(name=title, value=info_block, inline=False)
        
    async def obtain(self, role_manager: RoleManager, event_manager: EventManager, guild_id: int, member_id: int, beans_event_id: int = 0, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            beans_event_id,
            amount
        )
    
    async def use(self, role_manager: RoleManager, event_manager: EventManager, guild_id: int, member_id: int, amount: int = 1):
        event_manager.dispatch_inventory_event(
            datetime.datetime.now(), 
            guild_id,
            member_id,
            self.get_type(),
            0,
            -amount
        )
        
        return self.value