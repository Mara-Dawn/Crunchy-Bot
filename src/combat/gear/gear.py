import discord
from discord.ext import commands
from items.item import Item
from items.types import ItemGroup, ItemType, ShopCategory


class Gear(Item):

    def __init__(
        self,
        name: str, 
        type: ItemType,
        description: str,
        information: str,
        emoji: str,
        cost: int,
        
        weight: int = None,
        permanent: bool = False,
        secret: bool = False,
    ):
        super().__init__(
            name=name,
            type=type,
            group=ItemGroup.GEAR,
            shop_category=ShopCategory.GEAR,
            description=description,
            information=information,
            emoji=emoji,
            cost=cost,
            value=None,
            hide_in_shop=True,
            weight=weight,
            permanent=permanent,
            secret=secret
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
