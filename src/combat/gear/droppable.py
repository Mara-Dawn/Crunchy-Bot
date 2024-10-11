import discord

from combat.enchantments.types import EnchantmentType
from combat.gear.types import Base, EquipmentSlot, GearBaseType, Rarity
from combat.skills.types import SkillType


class DroppableBase:

    def __init__(
        self,
        name: str,
        base_type: Base,
        slot: EquipmentSlot,
        type: GearBaseType | SkillType | EnchantmentType,  # noqa: F821
        min_level: int,
        max_level: int,
        weight: int = None,
        droppable: bool = True,
        uniques: list[GearBaseType | SkillType | EnchantmentType] = None,
        author: str = None,
        special: str | None = None,
    ):
        self.name = name
        self.base_type = base_type
        self.type = type
        self.slot = slot
        self.min_level = min_level
        self.max_level = max_level
        self.weight = weight
        self.droppable = droppable
        if self.weight is None:
            self.weight = 100

        self.uniques = uniques
        if self.uniques is None:
            self.uniques = []

        self.special = special

        self.author = author
        if self.author is None:
            self.author = "Mara"


class Droppable:

    RARITY_COLOR_MAP = {
        Rarity.DEFAULT: "[30m",  # grey
        Rarity.COMMON: "[38m",  # white
        Rarity.UNCOMMON: "[36m",  # cyan
        Rarity.RARE: "[34m",  # blue
        Rarity.LEGENDARY: "[33m",  # yellow
        Rarity.UNIQUE: "[31m",  # red
    }

    RARITY_NAME_COLOR_MAP = {
        Rarity.DEFAULT: "[1;38m",
        Rarity.COMMON: "[1;38m",
        Rarity.UNCOMMON: "[1;36m",
        Rarity.RARE: "[1;34m",
        Rarity.LEGENDARY: "[1;33m",
        Rarity.UNIQUE: "[1;31m",
    }

    RARITY_COLOR_HEX_MAP = {
        Rarity.DEFAULT: discord.Color.dark_gray(),
        Rarity.COMMON: discord.Color(int("ffffff", 16)),
        Rarity.UNCOMMON: discord.Color(int("2aa198", 16)),
        Rarity.RARE: discord.Color(int("268bd2", 16)),
        Rarity.LEGENDARY: discord.Color(int("b58900", 16)),
        Rarity.UNIQUE: discord.Color(int("a43033", 16)),
    }

    RARITY_SORT_MAP = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 2,
        Rarity.RARE: 3,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 5,
    }

    def __init__(
        self,
        name: str,
        base: DroppableBase,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        level: int,
        rarity: Rarity,
        base_value: int = 1,
        image: str = None,
        image_path: str = None,
        image_url: str = None,
    ):
        self.name = name
        self.base = base
        self.type = type
        self.description = description
        self.information = information
        self.slot = slot
        self.level = level
        self.rarity = rarity
        self.image = image
        self.image_path = image_path
        self.image_url = image_url
        self.scaling = base_value

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        max_width: int = 44,
    ) -> discord.Embed:
        pass
