import discord
from combat.gear.types import GearRarity, GearSlot
from discord.ext import commands
from items.item import Item
from items.types import ItemGroup, ShopCategory


class GearBase:

    def __init__(
        self,
        name: str, 
        description: str,
        information: str,
        emoji: str,
        cost: int,
        slot: GearSlot,
        min_level: int,
        max_level: int,
        
        weight: int = None,
        permanent: bool = False,
        secret: bool = False,
    ):
        self.name = name
        self.description = description
        self.information = information
        self.emoji = emoji
        self.cost = cost
        self.slot = slot
        self.min_level = min_level
        self.max_level = max_level

        self.weight = weight
        if self.weight is None:
            self.weight = max(self.cost, 100)
        self.permanent = permanent
        self.secret = secret

class Gear(Item):

    def __init__(
        self,
        name: str, 
        base: GearBase,
        rarity: GearRarity,
        level: int,

    ):
        super().__init__(
            name=name,
            type=None,
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=base.description,
            information=base.information,
            emoji=base.emoji,
            cost=base.cost,
            value=None,
            hide_in_shop=True,
            weight=base.weight,
            permanent=base.permanent,
            secret=base.secret
        )
    
    def get_embed(self, bot: commands.Bot, color=None, amount_in_cart: int = 1, show_price = True, show_info: bool = False) -> discord.Embed:
        emoji = self.emoji
        if isinstance(self.emoji, int):
            emoji = str(bot.get_emoji(self.emoji))

        if color is None:
            color=discord.Colour.purple()

        title = f'> ~* {emoji} {self.name} {emoji}  *~'

        if self.permanent:
            title = f'> ~* {emoji} *{self.name}* {emoji} *~'

        description = self.description
        max_width = 53
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += ' '*spacing

        suffix = ''
        spacing = 0
        if show_price:    
            if self.permanent:
                suffix = f'🅱️[34m{self.cost*amount_in_cart}'
                suffix_len = len(suffix) - 5
            else:
                suffix = f'🅱️{self.cost*amount_in_cart}'
                suffix_len = len(suffix)
            spacing = max_width - suffix_len 
        info_block = f'```python\n"{description}"\n\n{' '*spacing}{suffix}```'

        if self.permanent:
            info_block = f'```ansi\n[33m"{description}"[0m\n\n{' '*spacing}{suffix}```'
        
        if show_info:
            info_block += f'```ansi\n[37m{self.information}```'
        
        embed = discord.Embed(title=title, description=info_block, color=color)
        
        return embed
    
    def add_to_embed(self, bot: commands.Bot, embed: discord.Embed, max_width: int, count: int=None, show_price: bool = False, name_suffix: str='', disabled: bool = False, show_info: bool = False) -> None:
        emoji = self.emoji
        if isinstance(self.emoji, int):
            emoji = str(bot.get_emoji(self.emoji))

        title = f'> ~*  {emoji} {self.name} {emoji}  *~ {name_suffix}'

        if self.permanent:
            title = f'> ~* {emoji} *{self.name}* {emoji} *~ {name_suffix}'

        description = self.description
        
        prefix = ''
        suffix = ''

        if self.permanent:
            if show_price:
                if count is None:
                    suffix = f'🅱️[34m{self.cost}'
                else:
                    prefix = f'owned: [34m{count}[0m'
                    suffix = f'🅱️[34m{self.cost}'
            else:
                if count is not None:
                    if disabled:
                        prefix = "[DISABLED]"
                    suffix = f'amount: [34m{count}'

            suffix_len = len(suffix) - 5
            prefix_len = max(0, len(prefix) - 5)

            spacing = max_width - prefix_len - suffix_len
            info_block = f'```ansi\n[33m"{description}"[0m\n\n{prefix}{' '*spacing}{suffix}```'
        else:
            if show_price:
                if count is None:
                    suffix = f'🅱️{self.cost}'
                else:
                    prefix = f'owned: {count}'
                    suffix = f'🅱️{self.cost}'
            else:
                if count is not None:
                    if disabled:
                        prefix = "[DISABLED]"
                    suffix = f'amount: {count}'

            suffix_len = len(suffix) 
            prefix_len = len(prefix)

            spacing = max_width - prefix_len - suffix_len
            info_block = f'```python\n"{description}"\n\n{prefix}{' '*spacing}{suffix}```'
        
        if show_info:
            info_block += f'```ansi\n[37m{self.information}```'

        
        embed.add_field(name=title, value=info_block, inline=False)
