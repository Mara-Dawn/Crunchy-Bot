import discord
from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import (
    Base,
    EnchantmentType,
    EquipmentSlot,
    GearBaseType,
    GearModifierType,
    Rarity,
)
from combat.skills.types import SkillEffect, SkillType


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


class GearBase(DroppableBase):

    DEFAULT_IMAGE_PATH = "img/gear/default/"
    IMAGE_NAMES = {
        EquipmentSlot.WEAPON: "weapon.png",
        EquipmentSlot.HEAD: "head.png",
        EquipmentSlot.BODY: "body.png",
        EquipmentSlot.LEGS: "legs.png",
        EquipmentSlot.ACCESSORY: "accessory.png",
    }

    def __init__(
        self,
        name: str,
        type: GearBaseType,
        description: str,
        information: str,
        slot: EquipmentSlot,
        min_level: int,
        max_level: int,
        modifiers: list[GearModifierType],
        skills: list[SkillType] = None,
        scaling: int = 1,
        weight: int = None,
        droppable: bool = True,
        permanent: bool = False,
        secret: bool = False,
        image: str = None,
        image_path: str = None,
    ):
        super().__init__(
            base_type=Base.GEAR,
            type=type,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
        )
        self.name = name
        self.type = type
        self.description = description
        self.information = information
        self.modifiers = modifiers
        self.image = image
        self.image_path = image_path

        self.skills = skills
        if self.skills is None:
            self.skills = []

        self.scaling = scaling
        self.permanent = permanent
        self.secret = secret

        if self.image is None:
            self.image = self.IMAGE_NAMES[self.slot]

        self.attachment_name = f"{self.type.name}_{self.image}"

        if self.image_path is None:
            self.image_path = self.DEFAULT_IMAGE_PATH

    def get_allowed_modifiers(self):
        match self.slot:
            case EquipmentSlot.HEAD:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.BODY:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.LEGS:
                return [
                    GearModifierType.DEFENSE,
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.WEAPON:
                return [
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.DEXTERITY,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]
            case EquipmentSlot.ACCESSORY:
                return [
                    GearModifierType.CONSTITUTION,
                    GearModifierType.HEALING,
                    GearModifierType.CRIT_DAMAGE,
                    GearModifierType.CRIT_RATE,
                    GearModifierType.ATTACK,
                    GearModifierType.MAGIC,
                ]


class Gear(Droppable):

    def __init__(
        self,
        name: str,
        base: GearBase,
        rarity: Rarity,
        level: int,
        modifiers: dict[GearModifierType, float],
        skills: list[SkillType],
        enchantments: list[Enchantment],
        locked: bool = False,
        id: int = None,
    ):
        super().__init__(
            name=name,
            base=base,
            type=base.type,
            description=base.description,
            information=base.information,
            slot=base.slot,
            rarity=rarity,
            level=level,
            scaling=base.scaling,
            image=base.image,
            image_path=base.image_path,
        )
        if self.name == "" or self.name is None:
            self.name = base.name
        self.base = base
        self.rarity = rarity
        self.level = level
        self.modifiers = modifiers

        index_map = {v: i for i, v in enumerate(GearModifierType.prio())}
        self.modifiers = dict(
            sorted(self.modifiers.items(), key=lambda pair: index_map[pair[0]])
        )

        self.skills = skills
        self.enchantments = enchantments
        self.locked = locked
        self.id = id

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        equipped: bool = False,
        show_locked_state: bool = False,
        max_width: int = 44,
    ) -> discord.Embed:
        color = self.RARITY_COLOR_HEX_MAP[self.rarity]

        name = f"~* {self.name} *~"
        suffix = ""
        if equipped:
            color = discord.Color.purple()
            suffix += " [EQUIPPED]"
        elif self.locked and show_locked_state:
            suffix += " [🔒]"

        description = f'"{self.description}"'

        name_rarity = self.rarity
        if self.rarity == Rarity.DEFAULT:
            name_rarity = Rarity.NORMAL

        info_block = "```ansi\n"
        info_block += f"{self.RARITY_COLOR_MAP[name_rarity]}{name}[0m{suffix}"
        spacing = " " * (
            max_width - len(name) - len(self.base.slot.value) - len(suffix) - 2
        )
        info_block += f"{spacing}[{self.base.slot.value}]"
        info_block += "```"

        prefixes = []
        suffixes = []

        if show_data and len(self.modifiers) > 0:
            max_len_pre = GearModifierType.max_name_len()
            max_len_suf = 8

            name = "Rarity"
            spacing = " " * (max_len_suf - len(self.rarity.value))
            rarity_line = f"{name}: {self.rarity.value}{spacing}"
            rarity_line_colored = f"{name}: {self.RARITY_COLOR_MAP[self.rarity]}{self.rarity.value}[0m{spacing}"
            suffixes.append((rarity_line_colored, len(rarity_line)))

            name = "Level"
            value = str(self.level)
            spacing = " " * (max_len_suf - len(value))
            level_line = f"{name}: {self.level}{spacing}"
            level_line_colored = f"{name}: [32m{self.level}[0m{spacing}"
            suffixes.append((level_line_colored, len(level_line)))

            if self.base.slot == EquipmentSlot.WEAPON and len(self.base.skills) > 0:
                damage_types = []
                for skill_type in self.base.skills:
                    if skill_type == SkillType.MAGIC_ATTACK:
                        effect = SkillEffect.MAGICAL_DAMAGE
                    elif skill_type in [
                        SkillType.NORMAL_ATTACK,
                        SkillType.HEAVY_ATTACK,
                    ]:
                        effect = SkillEffect.PHYSICAL_DAMAGE
                    if effect not in damage_types:
                        damage_types.append(effect)

                name = "Damage Type"
                if len(damage_types) > 1:
                    name += "s"
                value = ""
                value_colored = ""

                for damage_type in damage_types:
                    if value == "":
                        value += f"{damage_type.value}"
                        value_colored += f"[35m{damage_type.value}[0m"
                        spacing = " " * (max_len_pre - len(name))
                        damage_type_line = f"{spacing}{name}: {value}"
                        damage_type_line_colored = f"{spacing}{name}: {value_colored}"
                    else:
                        value += f"{damage_type.value}"
                        value_colored += f"[35m{damage_type.value}[0m"
                        spacing = " " * (max_len_pre)
                        damage_type_line = f"{spacing}  {value}"
                        damage_type_line_colored = f"{spacing}  {value_colored}"

                    prefixes.append((damage_type_line_colored, len(damage_type_line)))

            flat_damage_modifiers = {}

            for modifier_type, value in self.modifiers.items():
                if modifier_type in [
                    GearModifierType.WEAPON_DAMAGE_MIN,
                    GearModifierType.WEAPON_DAMAGE_MAX,
                ]:
                    flat_damage_modifiers[modifier_type] = value
                    continue
                name = modifier_type.value
                display_value = GearModifierType.display_value(modifier_type, value)
                spacing = " " * (max_len_pre - len(name))
                line = f"{spacing}{name}: {display_value}"
                line_colored = f"{spacing}{name}: [35m{display_value}[0m"
                prefixes.append((line_colored, len(line)))

            if len(flat_damage_modifiers) == 2:
                name = "Hit Damage"
                display_value_min = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MIN,
                    flat_damage_modifiers[GearModifierType.WEAPON_DAMAGE_MIN],
                )
                display_value_max = GearModifierType.display_value(
                    GearModifierType.WEAPON_DAMAGE_MAX,
                    flat_damage_modifiers[GearModifierType.WEAPON_DAMAGE_MAX],
                )
                spacing = " " * (max_len_pre - len(name))
                line = f"{spacing}{name}: {display_value_min} - {display_value_max}"
                line_colored = f"{spacing}{name}: [35m{display_value_min}[0m - [35m{display_value_max}[0m"
                prefixes.insert(0, (line_colored, len(line)))

            info_block += "```ansi\n"
            lines = max(len(suffixes), len(prefixes))

            for line in range(lines):
                prefix = ""
                suffix = ""
                len_prefix = 0
                len_suffix = 0
                if len(prefixes) > line:
                    len_prefix = prefixes[line][1]
                    prefix = prefixes[line][0]
                if len(suffixes) > line:
                    len_suffix = suffixes[line][1]
                    suffix = suffixes[line][0]

                spacing_width = max_width - len_prefix - len_suffix
                spacing = " " * spacing_width
                info_block += f"{prefix}{spacing}{suffix}\n"

            info_block += "```"

        info_block += f"```python\n{description}```"

        if show_info and len(self.information) > 0:
            info_block += f"```ansi\n[37m{self.information}```"

        embed = discord.Embed(title="", description=info_block, color=color)
        embed.set_thumbnail(url=f"attachment://{self.base.attachment_name}")
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