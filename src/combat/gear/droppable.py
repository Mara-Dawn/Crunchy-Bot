import discord
from combat.gear.types import Base, EquipmentSlot, GearBaseType, Rarity
from combat.skills.types import SkillType


class DroppableBase:

    def __init__(
        self,
        base_type: Base,
        slot: EquipmentSlot,
        type: GearBaseType | SkillType,  # noqa: F821
        min_level: int,
        max_level: int,
        weight: int = None,
    ):
        self.base_type = base_type
        self.type = type
        self.slot = slot
        self.min_level = min_level
        self.max_level = max_level
        self.weight = weight
        if self.weight is None:
            self.weight = 100


class Droppable:

    RARITY_COLOR_MAP = {
        Rarity.NORMAL: "[38m",  # ffffff
        Rarity.MAGIC: "[34m",  # 268bd2
        Rarity.RARE: "[33m",  # b58900
        Rarity.LEGENDARY: "[31m",  # #a43033
        Rarity.UNIQUE: "[36m",  # 2aa198
    }

    RARITY_COLOR_HEX_MAP = {
        Rarity.NORMAL: discord.Color(int("ffffff", 16)),
        Rarity.MAGIC: discord.Color(int("268bd2", 16)),
        Rarity.RARE: discord.Color(int("b58900", 16)),
        Rarity.LEGENDARY: discord.Color(int("a43033", 16)),
        Rarity.UNIQUE: discord.Color(int("2aa198", 16)),
    }

    RARITY_SORT_MAP = {
        Rarity.NORMAL: 0,
        Rarity.MAGIC: 1,
        Rarity.RARE: 2,
        Rarity.LEGENDARY: 3,
        Rarity.UNIQUE: 4,
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
        scaling: int = 1,
        image: str = None,
        image_path: str = None,
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
        self.scaling = scaling

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        max_width: int = 44,
    ) -> discord.Embed:
        pass
