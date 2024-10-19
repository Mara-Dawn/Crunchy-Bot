from dataclasses import dataclass
from typing import Any

import discord

from combat.gear.types import Rarity
from config import Config
from view.object.types import (
    BlockType,
    ObjectType,
    ValueColor,
    ValueColorBold,
    ValueColorHex,
    ValueType,
)


@dataclass
class DisplayBlock:

    def __init__(
        self,
        block_type: BlockType,
        content: str,
        length: int | None = None,
    ) -> None:
        self.block_type = block_type
        self.content = content
        if length is None:
            length = len(content)
        self.lenght = length

    def text(self, max_width: int) -> str:
        if self.content is None:
            return ""

        spacing = ""
        # if self.lenght < max_width:
        #     spacing = " " + "\u00a0" * (max_width - self.lenght)

        block = f"```{self.block_type.value}\n"
        block += self.content + spacing
        block += "```"

        return block

    @staticmethod
    def EMPTY() -> "DisplayBlock":
        return DisplayBlock(None, None)


@dataclass
class ObjectParameters:
    object_type: ObjectType
    name: str
    group: str
    description: str
    rarity: Rarity = None
    equipped: bool = False
    locked: bool = False
    information: str = None
    emoji: str = None
    suffix: str = None
    permanent: bool = False

    _max_width: int = None

    TITLE_PREFIX_MAP = {
        ObjectType.ITEM: "~*",
        ObjectType.GEAR: "-*",
        ObjectType.SKILL: "<-",
        ObjectType.ENCHANTMENT: "*#",
    }
    TITLE_SUFFIX_MAP = {
        ObjectType.ITEM: "*~",
        ObjectType.GEAR: "*-",
        ObjectType.SKILL: "->",
        ObjectType.ENCHANTMENT: "#*",
    }
    DEFAULT_WIDTH = {
        ObjectType.ITEM: Config.ITEM_MAX_WIDTH,
        ObjectType.GEAR: Config.COMBAT_EMBED_MAX_WIDTH,
        ObjectType.SKILL: Config.COMBAT_EMBED_MAX_WIDTH,
        ObjectType.ENCHANTMENT: Config.COMBAT_EMBED_MAX_WIDTH,
    }
    RARITY_NAME_COLOR_MAP = {
        Rarity.DEFAULT: ValueColorBold.WHITE.value,
        Rarity.COMMON: ValueColorBold.WHITE.value,
        Rarity.UNCOMMON: ValueColorBold.CYAN.value,
        Rarity.RARE: ValueColorBold.BLUE.value,
        Rarity.LEGENDARY: ValueColorBold.YELLOW.value,
        Rarity.UNIQUE: ValueColorBold.RED.value,
    }
    RARITY_COLOR_MAP = {
        Rarity.DEFAULT: ValueColor.GREY.value,
        Rarity.COMMON: ValueColor.WHITE.value,
        Rarity.UNCOMMON: ValueColor.CYAN.value,
        Rarity.RARE: ValueColor.BLUE.value,
        Rarity.LEGENDARY: ValueColor.YELLOW.value,
        Rarity.UNIQUE: ValueColor.RED.value,
    }
    INFORMATION_COLOR = ValueColor.WHITE.value
    RARITY_COLOR_HEX_MAP = {
        Rarity.DEFAULT: discord.Color(int(ValueColorHex.GREY, 16)),
        Rarity.COMMON: discord.Color(int(ValueColorHex.WHITE, 16)),
        Rarity.UNCOMMON: discord.Color(int(ValueColorHex.CYAN, 16)),
        Rarity.RARE: discord.Color(int(ValueColorHex.BLUE, 16)),
        Rarity.LEGENDARY: discord.Color(int(ValueColorHex.YELLOW, 16)),
        Rarity.UNIQUE: discord.Color(int(ValueColorHex.RED, 16)),
    }

    @property
    def max_width(self) -> int:
        if self._max_width is None:
            self._max_width = self.DEFAULT_WIDTH[self.object_type]
        return self._max_width

    @property
    def colored_title(self) -> str:
        title = self.raw_title

        if self.rarity is not None:
            color_start = self.RARITY_NAME_COLOR_MAP[self.rarity]
            title = f"{color_start}{title}{ValueColor.NONE.value}"
        else:
            title = f"{ValueColorBold.WHITE.value}{title}{ValueColor.NONE.value}"

        title += self.name_suffix
        return title

    @property
    def name_suffix(self) -> str:
        suffix = ""
        if self.equipped:
            suffix += " [EQ]"
        if self.locked:
            suffix += " [🔒]"
        if self.suffix is not None:
            suffix += f" - {self.suffix}"
        return suffix

    @property
    def raw_title(self) -> str:
        title = self.name

        if self.emoji is not None:
            title = f"{self.emoji} {title} {self.emoji}"

        prefix = self.TITLE_PREFIX_MAP[self.object_type]
        suffix = self.TITLE_SUFFIX_MAP[self.object_type]
        title = f"{prefix} {title} {suffix}"

        return title

    @property
    def title_suffix(self) -> str:
        return f"[{self.group}]"

    @property
    def title_spacer(self) -> str:
        width = (
            self.max_width
            - len(self.raw_title)
            - len(self.name_suffix)
            - len(self.title_suffix)
        )
        return " " * width

    @property
    def title_block(self) -> DisplayBlock:
        content = f"{self.colored_title}{self.title_spacer}{self.title_suffix}"
        raw_content = f"{self.raw_title}{self.title_spacer}{self.title_suffix}"
        return DisplayBlock(BlockType.ANSI, content, len(raw_content))

    @property
    def description_block(self) -> DisplayBlock:
        if self.permanent:
            content = f'"{ValueColorBold.YELLOW.value}{self.description}{ValueColor.NONE.value}"'
            return DisplayBlock(BlockType.ANSI, content, len(self.description))
        else:
            content = f'"{self.description}"'
            return DisplayBlock(BlockType.PYTHON, content, len(self.description))

    @property
    def information_block(self) -> DisplayBlock:
        if self.information is None:
            return DisplayBlock.EMPTY()

        content = f"{self.INFORMATION_COLOR}"
        content += f'"{self.information}"'
        content += f"{ValueColor.NONE.value}"

        return DisplayBlock(BlockType.ANSI, content, len(self.information))


class Affix:

    def __init__(
        self,
        name: str,
        value: Any,
        value_type: ValueType,
        value_color: ValueColor = ValueColor.PINK,
        pre: str = None,
        post: str = None,
    ) -> None:
        if name is None:
            name = ""
        self.name = name
        self.value = value
        self.value_type = value_type
        self.value_color = value_color
        self.max_length = 11
        self.pre = pre
        self.post = post

        if self.pre is None:
            self.pre = ""

        if self.post is None:
            self.post = ""

    def format_value(self, value: Any) -> str:
        display_value = ""
        match self.value_type:
            case ValueType.INT:
                display_value = f"{int(value)}"
            case ValueType.FLOAT:
                display_value = f"{value:.1f}"
            case ValueType.STRING:
                display_value = f"{value}"
            case ValueType.PERCENTAGE:
                display_value = value
                if display_value < 1:
                    display_value = display_value * 100
                display_value = f"{display_value:.1f}%"
            case ValueType.NONE:
                pass
        return display_value

    @property
    def display_value(self) -> str:
        return self.format_value(self.value)

    @property
    def separator(self) -> str:
        separator = ": "
        if self.name is None or len(self.name) == 0:
            separator = ""
        if self.display_value is None or len(self.display_value) == 0:
            separator = ""
        return separator

    @property
    def text(self) -> str:
        text = f"{self.name}{self.separator}{self.value}"
        return text

    @property
    def length(self) -> int:
        return len(self.text)


class Prefix(Affix):

    def __init__(
        self,
        name: str,
        value: Any,
        value_type: ValueType,
        value_color: ValueColor = ValueColor.PINK,
        pre: str = None,
        post: str = None,
        penalty: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            value=value,
            value_type=value_type,
            value_color=value_color,
            pre=pre,
            post=post,
        )
        self.penalty = penalty
        self.max_length = 11

    @property
    def length(self) -> int:
        return len(self.raw_text)

    @property
    def spacer(self) -> str:
        if self.name is None or len(self.name) == 0:
            spacing = " " * (self.max_length + len(self.separator))
        else:
            spacing = " " * (self.max_length - len(self.name))
        return spacing

    @property
    def raw_text(self) -> str:
        penalty = ""
        if self.penalty:
            penalty = " [!]"
        return f"{self.spacer}{self.name}{self.separator}{self.pre}{self.display_value}{self.post}{penalty}"

    @property
    def text(self) -> str:
        penalty = ""
        if self.penalty:
            penalty = f"{ValueColor.GREY.value}{penalty}{ValueColor.NONE.value}"
        colored_value = (
            f"{self.value_color.value}{self.display_value}{ValueColor.NONE.value}"
        )
        return f"{self.spacer}{self.name}{self.separator}{self.pre}{colored_value}{self.post}{penalty}"

    @staticmethod
    def EMPTY() -> "Prefix":
        return Prefix(None, None, value_type=ValueType.NONE)


class MultiPrefix(Prefix):

    def __init__(
        self,
        name: str,
        values: list[Any],
        value_separator: str,
        value_type: ValueType,
        value_color: ValueColor = ValueColor.PINK,
        pre: str = None,
        post: str = None,
        penalty: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            value=None,
            value_type=value_type,
            value_color=value_color,
            pre=pre,
            post=post,
            penalty=penalty,
        )
        self.values = values
        self.value_separator = value_separator

    @property
    def length(self) -> int:
        return len(self.raw_text)

    @property
    def display_value(self) -> str:
        display_values = []
        for value in self.values:
            display_values.append(self.format_value(value))

        display_value = self.value_separator.join(display_values)

        return display_value

    @property
    def raw_text(self) -> str:
        penalty = ""
        if self.penalty:
            penalty = " [!]"
        return f"{self.spacer}{self.name}{self.separator}{self.display_value}{penalty}"

    @property
    def text(self) -> str:
        penalty = ""
        if self.penalty:
            penalty = " [!]"
            penalty = f"{ValueColorBold.GREY.value}{penalty}{ValueColor.NONE.value}"

        display_values = []
        for value in self.values:
            formatted = self.format_value(value)
            colored = f"{self.value_color.value}{formatted}{ValueColor.NONE.value}"
            display_values.append(colored)

        display_value = self.value_separator.join(display_values)

        display_value = f"{self.pre}{display_value}{self.post}"

        return f"{self.spacer}{self.name}{self.separator}{display_value}{penalty}"


class Suffix(Affix):

    def __init__(
        self,
        name: str,
        value: Any,
        value_type: ValueType,
        value_color: ValueColor = ValueColor.PINK,
        pre: str = None,
        post: str = None,
    ) -> None:
        super().__init__(
            name=name,
            value=value,
            value_type=value_type,
            value_color=value_color,
            pre=pre,
            post=post,
        )
        self.max_length = 10

    @property
    def length(self) -> int:
        return len(self.raw_text)

    @property
    def spacer(self) -> str:
        return " " * (self.max_length - len(self.display_value) - len(self.post))

    @property
    def raw_text(self) -> str:
        return f"{self.name}{self.separator}{self.pre}{self.display_value}{self.post}{self.spacer}"

    @property
    def text(self) -> str:
        colored_value = (
            f"{self.value_color.value}{self.display_value}{ValueColor.NONE.value}"
        )
        return f"{self.name}{self.separator}{self.pre}{colored_value}{self.post}{self.spacer}"

    @staticmethod
    def EMPTY() -> "Suffix":
        return Suffix(None, None, value_type=ValueType.NONE)


class AffixBlock(DisplayBlock):

    def __init__(
        self,
        prefixes: list[Prefix],
        suffixes: list[Suffix],
        max_width: int,
    ) -> None:
        super().__init__(
            block_type=BlockType.ANSI,
            content="",
        )
        self.prefixes = prefixes
        self.suffixes = suffixes
        self.max_width = max_width

    def text(self, max_width: int = None) -> str:
        if self.content is None:
            return ""

        block = f"```{self.block_type}\n"
        block += self.content
        block += "```"

        lines = max(len(self.suffixes), len(self.prefixes))
        if lines <= 0:
            return ""

        affix_lines = []
        prefix_max = 11
        if len(self.prefixes) > 0:
            prefix_max = max(
                [
                    len(prefix.name)
                    for prefix in self.prefixes
                    if prefix.name is not None
                ]
            )

        for prefix in self.prefixes:
            prefix.max_length = prefix_max

        for line in range(lines):
            prefix = ""
            suffix = ""
            len_prefix = 0
            len_suffix = 0
            if len(self.prefixes) > line:
                len_prefix = self.prefixes[line].length
                prefix = self.prefixes[line].text
            if len(self.suffixes) > line:
                len_suffix = self.suffixes[line].length
                suffix = self.suffixes[line].text

            spacing_width = self.max_width - len_prefix - len_suffix
            spacing = " " * spacing_width
            affix_lines.append(f"{prefix}{spacing}{suffix}")

        self.content = "\n".join(affix_lines)
        self.lenght = len(self.content)
        return super().text(self.max_width)


class ObjectDisplay:

    def __init__(
        self,
        parameters: ObjectParameters,
        prefixes: list[Prefix],
        suffixes: list[Suffix],
        extra_displays: list["ObjectDisplay"] = None,
        extra_blocks: list[DisplayBlock] = None,
        thumbnail_url: str = None,
        author: str = None,
    ):
        self.parameters = parameters
        self.prefixes = prefixes
        self.suffixes = suffixes
        self.thumbnail_url = thumbnail_url
        self.author = author
        self.extra_displays = extra_displays
        self.extra_blocks = extra_blocks

        if self.extra_displays is None:
            self.extra_displays = []

        if self.extra_blocks is None:
            self.extra_blocks = []

        if self.author is None:
            self.author = "Mara"

        self.affix_block = AffixBlock(
            self.prefixes, self.suffixes, self.parameters.max_width
        )

    def get_embed_content(
        self, show_info: bool = False, show_title: bool = True, show_data: bool = True
    ) -> str:
        content = ""
        if show_title:
            content += self.parameters.title_block.text(
                max_width=self.parameters.max_width
            )
        if show_data:
            content += self.affix_block.text()
        content += self.parameters.description_block.text(
            max_width=self.parameters.max_width
        )
        if show_info:
            content += self.parameters.information_block.text(
                max_width=self.parameters.max_width
            )
        return content

    def get_embed(
        self,
        show_info: bool = False,
        show_title: bool = True,
        color: discord.Color = None,
    ) -> discord.Embed:
        content = self.get_embed_content(show_info=show_info, show_title=show_title)

        for block in self.extra_blocks:
            content += block.text(max_width=self.parameters.max_width)

        for object_data in self.extra_displays:
            content += object_data.get_embed_content(show_info=show_info)

        if color is None:
            color = discord.Colour.purple()

        if self.parameters.rarity is not None:
            color = ObjectParameters.RARITY_COLOR_HEX_MAP[self.parameters.rarity]

        embed = discord.Embed(title="", description=content, color=color)
        if self.thumbnail_url is not None:
            embed.set_thumbnail(url=self.thumbnail_url)
        embed.set_footer(text=f"by {self.author}")
        return embed
