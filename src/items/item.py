import discord
from discord.ext import commands

from config import Config
from datalayer.types import ItemTrigger
from forge.forgable import Forgeable
from items.types import ItemGroup, ItemType, ShopCategory
from view.object.embed import (
    AffixBlock,
    DisplayBlock,
    ObjectDisplay,
    ObjectParameters,
    Prefix,
    Suffix,
)
from view.object.types import (
    BlockType,
    ObjectType,
    ValueColor,
    ValueColorBold,
    ValueType,
)


class Item(Forgeable):

    def __init__(
        self,
        name: str,
        type: ItemType,
        group: ItemGroup,
        shop_category: ShopCategory,
        description: str,
        information: str,
        emoji: str,
        cost: int,
        value: int,
        view_class: str = None,
        allow_amount: bool = False,
        base_amount: int = 1,
        max_amount: int = None,
        trigger: list[ItemTrigger] = None,
        hide_in_shop: bool = False,
        weight: int = None,
        controllable: bool = False,
        useable: bool = False,
        permanent: bool = False,
        secret: bool = False,
        image_url: str = None,
    ):
        int_id = -1 if type is None else int.from_bytes(type.name.encode(), "little")
        super().__init__(
            name=name,
            id=int_id,
            forge_type=type,
            value=value,
            object_type=ObjectType.ITEM,
            emoji=emoji,
            image_url=image_url,
        )
        self.name = name
        self.type = type
        self.group = group
        self.shop_category = shop_category
        self.description = description
        self.information = information
        self.cost = cost
        self.value = value
        self.emoji = emoji
        self.view_class = view_class
        self.allow_amount = allow_amount
        self.base_amount = base_amount
        self.max_amount = max_amount
        self.trigger = trigger
        self.hide_in_shop = hide_in_shop
        self.weight = weight
        if self.weight is None:
            self.weight = max(self.cost, 100)
        self.controllable = controllable
        self.useable = useable
        self.permanent = permanent
        self.secret = secret
        self.image_url = image_url

    def activated(self, action: ItemTrigger):
        if self.trigger is None:
            return False
        return action in self.trigger

    def display(
        self,
        bot: commands.Bot = None,
        show_price: bool = False,
        count: int = None,
        name_suffix: str = None,
        disabled: bool = False,
    ) -> ObjectDisplay:
        emoji = self.emoji
        image_url = self.image_url
        if isinstance(self.emoji, int):
            emoji = None
            if image_url is None:
                image_url = str(bot.get_emoji(self.emoji).url)

        parameters = ObjectParameters(
            object_type=ObjectType.ITEM,
            name=self.name,
            group="Item",
            description=self.description,
            emoji=emoji,
            information=self.information,
            permanent=self.permanent,
            suffix=name_suffix,
        )
        extra_blocks: list[DisplayBlock] = []

        if show_price:
            if count is not None:
                prefix = Prefix("In Cart", count, ValueType.INT)
                suffix = Suffix("Total", f"🅱️{self.cost * count}", ValueType.STRING)
                extra_blocks.append(
                    AffixBlock([prefix], [suffix], parameters.max_width)
                )
            else:
                cost = f"🅱️{ValueColorBold.PINK.value}{self.cost}{ValueColor.NONE.value}"
                spacing = parameters.max_width - len(f" {self.cost}") - 1
                content = f"\n~{" "*spacing}{cost}"
                raw_content = f"\n~{" "*spacing}{self.cost}"
                extra_blocks.append(
                    DisplayBlock(BlockType.ANSI, content, len(raw_content))
                )
        else:
            if count:
                if disabled:
                    prefix = Prefix(
                        "State",
                        "ENABLED",
                        ValueType.STRING,
                        value_color=ValueColor.GREEN,
                    )
                else:
                    prefix = Prefix(
                        "State",
                        "DISABLED",
                        ValueType.STRING,
                        value_color=ValueColor.RED,
                    )
                suffix = Suffix("Amount", count, ValueType.INT)
                extra_blocks.append(
                    AffixBlock([prefix], [suffix], parameters.max_width)
                )

        return ObjectDisplay(
            parameters=parameters,
            prefixes=[],
            suffixes=[],
            extra_blocks=extra_blocks,
            thumbnail_url=image_url,
        )

    def get_embed(
        self,
        bot: commands.Bot = None,
        show_price: bool = False,
        show_info: bool = False,
        show_title: bool = True,
        color: discord.Color = None,
        count: int = None,
        name_suffix: str = None,
        disabled: bool = False,
    ) -> discord.Embed:
        display = self.display(
            bot=bot,
            show_price=show_price,
            count=count,
            name_suffix=name_suffix,
            disabled=disabled,
        )
        return display.get_embed(
            show_title=show_title, show_info=show_info, color=color
        )

    def add_to_embed(
        self,
        bot: commands.Bot,
        embed: discord.Embed,
        max_width: int = None,
        count: int = None,
        show_price: bool = False,
        name_suffix: str = "",
        disabled: bool = False,
        show_info: bool = False,
    ) -> None:
        if max_width is None:
            max_width = Config.ITEM_MAX_WIDTH
        emoji = self.emoji
        if isinstance(self.emoji, int):
            emoji = str(bot.get_emoji(self.emoji))

        title = f"> ~*  {emoji} {self.name} {emoji}  *~ {name_suffix}"

        if self.permanent:
            title = f"> ~* {emoji} *{self.name}* {emoji} *~ {name_suffix}"

        description = self.description

        prefix = ""
        suffix = ""

        if self.permanent:
            if show_price:
                if count is None:
                    suffix = f"🅱️[34m{self.cost}"
                else:
                    prefix = f"owned: [34m{count}[0m"
                    suffix = f"🅱️[34m{self.cost}"
            else:
                if count is not None:
                    if disabled:
                        prefix = "[DISABLED]"
                    suffix = f"amount: [34m{count}"

            suffix_len = len(suffix) - 5
            prefix_len = max(0, len(prefix) - 5)

            spacing = max_width - prefix_len - suffix_len
            info_block = (
                f'```ansi\n[33m"{description}"[0m\n\n{prefix}{' '*spacing}{suffix}```'
            )
        else:
            if show_price:
                if count is None:
                    suffix = f"🅱️{self.cost}"
                else:
                    prefix = f"owned: {count}"
                    suffix = f"🅱️{self.cost}"
            else:
                if count is not None:
                    if disabled:
                        prefix = "[DISABLED]"
                    suffix = f"amount: {count}"

            suffix_len = len(suffix)
            prefix_len = len(prefix)

            spacing = max_width - prefix_len - suffix_len
            info_block = (
                f'```python\n"{description}"\n\n{prefix}{' '*spacing}{suffix}```'
            )

        if show_info:
            info_block += f"```ansi\n[37m{self.information}```"

        embed.add_field(name=title, value=info_block, inline=False)
