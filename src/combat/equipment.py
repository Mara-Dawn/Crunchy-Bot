import discord

from combat.enchantments.enchantment import EffectEnchantment
from combat.gear.default_gear import (
    DefaultAccessory1,
    DefaultAccessory2,
    DefaultCap,
    DefaultPants,
    DefaultShirt,
    DefaultStick,
)
from combat.gear.gear import Gear
from combat.gear.types import CharacterAttribute, GearModifierType
from config import Config


class CharacterEquipment:

    def __init__(
        self,
        member_id: int,
        level: int,
        weapon: Gear = None,
        head_gear: Gear = None,
        body_gear: Gear = None,
        leg_gear: Gear = None,
        accessory_1: Gear = None,
        accessory_2: Gear = None,
    ):
        self.member_id = member_id
        self.weapon = weapon
        self.head_gear = head_gear
        self.body_gear = body_gear
        self.leg_gear = leg_gear
        self.accessory_1 = accessory_1
        self.accessory_2 = accessory_2

        if self.weapon is None:
            self.weapon = DefaultStick()

        if self.head_gear is None:
            self.head_gear = DefaultCap()

        if self.body_gear is None:
            self.body_gear = DefaultShirt()

        if self.leg_gear is None:
            self.leg_gear = DefaultPants()

        if self.accessory_1 is None:
            self.accessory_1 = DefaultAccessory1()

        if self.accessory_2 is None:
            self.accessory_2 = DefaultAccessory2()

        self.gear: list[Gear] = [
            self.weapon,
            self.head_gear,
            self.body_gear,
            self.leg_gear,
            self.accessory_1,
            self.accessory_2,
        ]

        self.enchantments: list[EffectEnchantment] = []
        for gear in self.gear:
            if gear.enchantments is not None:
                self.enchantments.extend(gear.enchantments)

        self.attributes: dict[CharacterAttribute, float] = {
            CharacterAttribute.PHYS_DAMAGE_INCREASE: 0,
            CharacterAttribute.MAGIC_DAMAGE_INCREASE: 0,
            CharacterAttribute.HEALING_BONUS: 0,
            CharacterAttribute.CRIT_RATE: 0.1,
            CharacterAttribute.CRIT_DAMAGE: 1.5,
            CharacterAttribute.DAMAGE_REDUCTION: 0,
            CharacterAttribute.MAX_HEALTH: 250,
        }

        self.gear_modifiers: dict[GearModifierType, float] = {}

        for type in GearModifierType:
            self.gear_modifiers[type] = 0

        for item in self.gear:
            if item is None:
                continue
            for modifier_type, modifier in item.modifiers.items():
                self.gear_modifiers[modifier_type] += modifier

        self.attributes[CharacterAttribute.PHYS_DAMAGE_INCREASE] += (
            self.gear_modifiers[GearModifierType.ATTACK] / 100
        )
        self.attributes[CharacterAttribute.MAGIC_DAMAGE_INCREASE] += (
            self.gear_modifiers[GearModifierType.MAGIC] / 100
        )
        self.attributes[CharacterAttribute.CRIT_RATE] += (
            self.gear_modifiers[GearModifierType.CRIT_RATE] / 100
        )
        self.attributes[CharacterAttribute.CRIT_DAMAGE] += (
            self.gear_modifiers[GearModifierType.CRIT_DAMAGE] / 100
        )
        self.attributes[CharacterAttribute.DAMAGE_REDUCTION] += (
            self.gear_modifiers[GearModifierType.DEFENSE] / 100
        )
        self.attributes[CharacterAttribute.MAX_HEALTH] += (
            5 * self.gear_modifiers[GearModifierType.CONSTITUTION]
        ) + Config.CHARACTER_LVL_HP_INCREASE * (level - 1)
        self.attributes[CharacterAttribute.HEALING_BONUS] += (
            self.gear_modifiers[GearModifierType.HEALING] / 100
        )

    def get_embed(
        self,
        title: str,
        max_width: int = 44,
    ) -> None:
        description = "See how your gear affects your characters performance in combat."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing
        description = f"```\n{description}```"

        embed = discord.Embed(
            title=title, description=description, color=discord.Color.purple()
        )

        modifier_title = "Total Gear Modifiers:"
        info_block = "```ansi\n"
        max_len = GearModifierType.max_name_len()
        for modifier_type, value in self.gear_modifiers.items():
            if GearModifierType.is_unique_modifier(modifier_type) and value == 0:
                continue
            name = modifier_type.value
            display_value = GearModifierType.display_value(modifier_type, value)
            spacing = " " * (max_len - len(name))
            line_colored = f"{spacing}{name}: [35m{display_value}[0m\n"
            info_block += line_colored
        info_block += "```"
        embed.add_field(name=modifier_title, value=info_block, inline=True)

        attribute_title = "Character Attributes:"
        info_block = "```ansi\n"
        max_len = CharacterAttribute.max_name_len()
        for attribute_type, value in self.attributes.items():
            name = attribute_type.value
            display_value = CharacterAttribute.display_value(attribute_type, value)
            spacing = " " * (max_len - len(name))
            line_colored = f"{spacing}{name}: [35m{display_value}[0m\n"
            info_block += line_colored
        info_block += "```"
        embed.add_field(name=attribute_title, value=info_block, inline=True)

        return embed

    def add_to_embed(
        self,
        embed: discord.Embed,
        title: str,
        max_width: int = 44,
    ) -> None:

        info_block = "```ansi\n"

        info_block += "-" * max_width + "\n"
        info_block += "Total Gear Modifiers:\n"
        info_block += "-" * max_width + "\n"

        max_len = GearModifierType.max_name_len()
        for modifier_type, value in self.gear_modifiers.items():
            name = modifier_type.value
            spacing = " " * (max_len - len(name))
            line_colored = f"{spacing}{name}: [35m{value}[0m\n"
            info_block += line_colored

        info_block += "-" * max_width + "\n"
        info_block += "Character Attributes:\n"
        info_block += "-" * max_width + "\n"

        max_len = CharacterAttribute.max_name_len()
        for attribute_type, value in self.attributes.items():
            name = attribute_type.value
            spacing = " " * (max_len - len(name))
            line_colored = f"{spacing}{name}: [35m{value}[0m\n"
            info_block += line_colored

        info_block += "```"

        embed.add_field(name=title, value=info_block, inline=False)
