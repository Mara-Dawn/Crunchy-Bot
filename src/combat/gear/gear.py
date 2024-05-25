import discord
from combat.gear.types import (
    EnchantmentType,
    GearBaseType,
    GearModifierType,
    GearRarity,
    GearSlot,
)
from combat.skills.types import SkillType
from items.item import Item
from items.types import ItemGroup, ShopCategory


class Enchantment:

    def __init__(
        self,
        name: str,
        type: EnchantmentType,
        description: str,
        information: str,
        min_level: int,
        max_level: int,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.min_level = min_level
        self.max_level = max_level


class GearBase:

    DEFAULT_IMAGE_PATH = "img/gear/default/"
    IMAGE_NAMES = {
        GearSlot.WEAPON: "weapon.png",
        GearSlot.HEAD: "head.png",
        GearSlot.BODY: "body.png",
        GearSlot.LEGS: "legs.png",
        GearSlot.ACCESSORY: "accessory.png",
    }

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: GearSlot,
        min_level: int,
        max_level: int,
        modifiers: list[GearModifierType],
        skills: list[SkillType] = None,
        scaling: int = 1,
        cost: int = 0,
        weight: int = None,
        permanent: bool = False,
        secret: bool = False,
        image: str = None,
        image_path: str = None,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.cost = cost
        self.slot = slot
        self.min_level = min_level
        self.max_level = max_level
        self.modifiers = modifiers
        self.image = image
        self.image_path = image_path

        self.skills = skills
        if self.skills is None:
            self.skills = []

        self.scaling = scaling
        self.weight = weight
        if self.weight is None:
            self.weight = max(self.cost, 100)
        self.permanent = permanent
        self.secret = secret

        self.emoji = ""
        match self.slot:
            case GearSlot.HEAD:
                self.emoji = "⛑️"
            case GearSlot.BODY:
                self.emoji = "🥼"
            case GearSlot.LEGS:
                self.emoji = "👖"
            case GearSlot.WEAPON:
                self.emoji = "⚔"
            case GearSlot.ACCESSORY:
                self.emoji = "💍"

        if self.image is None:
            self.image = self.IMAGE_NAMES[self.slot]
        
        if self.image_path is None:
            self.image_path = self.DEFAULT_IMAGE_PATH


    def get_allowed_modifiers(self):
        match self.slot:
            case GearSlot.HEAD:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case GearSlot.BODY:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case GearSlot.LEGS:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case GearSlot.WEAPON:
                return [
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case GearSlot.ACCESSORY:
                return [
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]


class Gear(Item):

    RARITY_COLOR_MAP = {
        GearRarity.NORMAL: "[38m",  # ffffff
        GearRarity.MAGIC: "[34m",  # 268bd2
        GearRarity.RARE: "[33m",  # b58900
        GearRarity.LEGENDARY: "[31m",  # #a43033
        GearRarity.UNIQUE: "[36m",  # 2aa198
    }

    RARITY_COLOR_HEX_MAP = {
        GearRarity.NORMAL: discord.Color(int("ffffff", 16)),
        GearRarity.MAGIC: discord.Color(int("268bd2", 16)),
        GearRarity.RARE: discord.Color(int("b58900", 16)),
        GearRarity.LEGENDARY: discord.Color(int("a43033", 16)),
        GearRarity.UNIQUE: discord.Color(int("2aa198", 16)),
    }

    def __init__(
        self,
        name: str,
        base: GearBase,
        rarity: GearRarity,
        level: int,
        modifiers: dict[GearModifierType, float],
        skills: list[SkillType],
        enchantments: list[Enchantment],
        id: int = None,
    ):
        if name == "":
            name = base.name
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
            secret=base.secret,
        )
        self.base = base
        self.rarity = rarity
        self.level = level
        self.modifiers = modifiers
        self.skills = skills
        self.enchantments = enchantments
        self.id = id

    def get_embed(
        self,
        title: str = None,
        show_data: bool = True,
        show_info: bool = False,
        max_width: int = 44,
    ) -> discord.Embed:
        if title is None:
            title = self.base.slot.value

        title = f"> {title} Slot"

        description = f'"{self.description}"'
        color = self.RARITY_COLOR_HEX_MAP[self.rarity]

        info_block = "```ansi\n"
        info_block += f"{self.RARITY_COLOR_MAP[self.rarity]}~* {self.name} *~[0m"
        spacing = " " * (max_width - len(self.name) - len(self.base.slot.value) - 8)
        info_block += f"{spacing}[{self.base.slot.value}]"
        info_block += "```"

        if show_data and len(self.modifiers) > 0:
            max_len = GearModifierType.max_name_len()
            info_block += "```ansi\n"

            name = "Rarity"
            spacing = " " * (max_len - len(name))
            line_colored = f"{spacing}{name}: {self.RARITY_COLOR_MAP[self.rarity]}{self.rarity.value}[0m\n"
            info_block += line_colored

            for modifier_type, value in self.modifiers.items():
                name = modifier_type.value
                spacing = " " * (max_len - len(name))
                line_colored = f"{spacing}{name}: [35m{value}[0m\n"
                info_block += line_colored

            info_block += "```"

        info_block += f"```python\n{description}```"

        if show_info and len(self.information) > 0:
            info_block += f"```ansi\n[37m{self.information}```"

        embed = discord.Embed(title=title, description=info_block, color=color)
        embed.set_thumbnail(url=f"attachment://{self.base.image}")
        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        title: str = None,
        show_data: bool = True,
        show_info: bool = False,
        max_width: int = 44,
    ) -> None:
        if title is None:
            title = self.base.slot.value
        description = f'"{self.description}"'

        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        info_block = f"```python\n{description}```"

        if show_data:
            max_len = GearModifierType.max_name_len()

            info_block += "```ansi\n"
            info_block += f"{self.RARITY_COLOR_MAP[self.rarity]}{self.name}[0m\n"
            info_block += "-" * max_width + "\n"
            info_block += f"{self.base.slot.value}\n"
            info_block += "-" * max_width + "\n"

            for modifier_type, value in self.modifiers.items():
                name = modifier_type.value
                spacing = " " * (max_len - len(name))
                line_colored = f"{spacing}{name}: [35m{value}[0m\n"
                info_block += line_colored

            info_block += "```"

        if show_info:
            info_block += f"```ansi\n[37m{self.skill.information}```"

        embed.add_field(name=title, value=info_block, inline=False)
