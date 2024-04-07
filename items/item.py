import discord

from datalayer.types import ItemTrigger
from items.types import ItemGroup, ItemType, ShopCategory


class Item:

    def __init__(
        self,
        name: str, 
        item_type: ItemType,
        group: ItemGroup,
        shop_category: ShopCategory,
        description: str,
        emoji: str,
        cost: int,
        value: int,
        view_class: str = None,
        allow_amount: bool = False,
        base_amount: int = 1,
        max_amount: int = None,
        trigger: list[ItemTrigger] = None
    ):
        self.name = name
        self.type = item_type
        self.group = group
        self.shop_category = shop_category
        self.description = description
        self.cost = cost
        self.value = value
        self.emoji = emoji
        self.view_class = view_class
        self.allow_amount = allow_amount
        self.base_amount = base_amount
        self.max_amount = max_amount
        self.trigger = trigger
    
    def activated(self, action: ItemTrigger):
        if self.trigger is None:
            return False
        return action in self.trigger
    
    def get_embed(self, color=None, amount_in_cart: int = 1) -> discord.Embed:
        if color is None:
            color=discord.Colour.purple()
        title = f'> {self.emoji} {self.name} {self.emoji}'
        description = self.description
        max_width = 53
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        suffix = f'🅱️{self.cost*amount_in_cart}'
        spacing = max_width - len(suffix)
        info_block = f'```python\n"{description}"\n\n{' '*spacing}{suffix}```'
        
        embed = discord.Embed(title=title, description=info_block, color=color)
        
        return embed
    
    def add_to_embed(self, embed: discord.Embed, max_width: int, count: int=None, name_suffix: str='') -> None:
        title = f'> ~*  {self.emoji} {self.name} {self.emoji}  *~ {name_suffix}'
        description = self.description
        
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing
            
        suffix = f'🅱️{self.cost}' if count is None else f'amount: {count}'
        spacing = max_width - len(suffix)
        info_block = f'```python\n"{description}"\n\n{' '*spacing}{suffix}```'
        
        embed.add_field(name=title, value=info_block, inline=False)
