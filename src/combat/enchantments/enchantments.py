import random

from combat.effects.types import EffectTrigger
from combat.enchantments.enchantment import (
    BaseCraftingEnchantment,
    BaseEffectEnchantment,
    BaseEnchantment,
)
from combat.enchantments.types import (
    EnchantmentEffect,
    EnchantmentFilterFlags,
    EnchantmentType,
)
from combat.gear.types import EquipmentSlot, Rarity
from combat.skills.skill import BaseSkill
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillEffect, SkillType
from view.object.types import ValueType

# Enchantments used for internal logic only


class Empty(BaseEnchantment):

    def __init__(self):
        super().__init__(
            name="Empty",
            enchantment_type=EnchantmentType.EMPTY,
            description="This enchantment slot is currently empty.",
            information="",
            enchantment_effect=EnchantmentEffect.EFFECT,
            droppable=False,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Crafting(BaseEnchantment):

    def __init__(self):
        super().__init__(
            name="Dummy",
            enchantment_type=EnchantmentType.CRAFTING,
            description="Used to group up crafting enchants in the enchantment view.",
            information="",
            enchantment_effect=EnchantmentEffect.CRAFTING,
            droppable=False,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


# Crafting Enchantments


class Chaos(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Chaos Bean",
            min_level=4,
            enchantment_type=EnchantmentType.CHAOS,
            description="Randomly rerolls all modifiers on a gear piece of any rarity.",
            information="",
            rarities=[Rarity.UNIQUE],
            droppable=True,
            weight=80,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Divine(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Divine Bean",
            min_level=5,
            enchantment_type=EnchantmentType.DIVINE,
            description=(
                "Rerolls all modifier values on a gear piece of any rarity. "
                "The modifiers themselves will stay the same."
            ),
            information="",
            rarities=[Rarity.UNIQUE],
            droppable=True,
            weight=20,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Exalted(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Exalted Bean",
            min_level=4,
            enchantment_type=EnchantmentType.EXALTED,
            description=(
                "Adds a random modifier to the item and upgrades it to the next rarity. "
                "Only works on gear of the same rarity as this item."
            ),
            information="",
            rarities=[Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE],
            filter_flags=[EnchantmentFilterFlags.MATCH_RARITY],
            droppable=True,
            weight=30,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Chance(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Chance Bean",
            min_level=4,
            enchantment_type=EnchantmentType.CHANCE,
            description=(
                "Upgrades a common item to a random rarity and rerolls "
                "its modifiers."
            ),
            information="",
            rarities=[Rarity.UNIQUE],
            filter_flags=[EnchantmentFilterFlags.MATCH_COMMON_RARITY],
            droppable=True,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Crangle(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            min_level=5,
            name="Crangle Bean",
            enchantment_type=EnchantmentType.CRANGLE,
            description=(
                "Crangles an item, rerolling its modifiers with unexpected outcomes. "
                "New modifiers include ones the base item could'nt normally roll. "
                "New modifiers can roll higher than normal. "
                "New modifiers can be negative. "
                "Crangled items can not be modifed any further. "
            ),
            information="",
            rarities=[Rarity.UNIQUE],
            droppable=True,
            weight=50,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


# Effect Enchantments


class DeathSave(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            min_level=4,
            name="Cheat Death",
            enchantment_type=EnchantmentType.DEATH_SAVE,
            description="Allows you to survive lethal damage.",
            information="",
            slot=EquipmentSlot.ACCESSORY,
            stacks=1,
            droppable=True,
            value=0.2,
            cooldown=2,
            skill_effect=SkillEffect.HEALING,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_DEATH],
            consumed=[EffectTrigger.ON_DEATH],
            emoji="💞",
        )


class SkillStacksProxy(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            min_level=4,
            name="Skill Stacks",
            enchantment_type=EnchantmentType.SKILL_STACKS,
            description="",
            information="",
            slot=EquipmentSlot.ARMOR,
            stacks=None,
            droppable=True,
            value=1,
            skill_effect=SkillEffect.NOTHING,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.SKILL_CHARGE],
            consumed=[],
            emoji="",
            value_label="Charges",
            value_type=ValueType.INT,
        )


class SkillStacks(SkillStacksProxy):

    SKILLS = [
        SkillType.SECOND_HEART,
        SkillType.FAMILY_PIZZA,
        SkillType.DOPE_SHADES,
        SkillType.FORESIGHT,
        SkillType.LOOKSMAXXING,
        SkillType.GIGA_BONK,
        SkillType.SLICE_N_DICE,
        SkillType.COOL_CUCUMBER,
        SkillType.POCKET_SAND,
        SkillType.BLOOD_RAGE,
        SkillType.PHYSICAL_MISSILE,
        SkillType.FINE_ASS,
        SkillType.COLORFUL_VASE,
        SkillType.NEURON_ACTIVATION,
        SkillType.FIRE_BALL,
        SkillType.MAGIC_MISSILE,
        SkillType.PARTY_DRUGS,
        SkillType.SPECTRAL_HAND,
        SkillType.ICE_BALL,
    ]

    RARITY_VALUE_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.5,
        Rarity.RARE: 2,
        Rarity.LEGENDARY: 2.5,
    }

    MIN_RARITY_LVL = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 0,
        Rarity.UNCOMMON: 1,
        Rarity.RARE: 2,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 2,
    }

    def __init__(
        self,
        level: int,
        skill_type: SkillType | None = None,
    ):
        super().__init__()

        if skill_type is None:
            available: list[BaseSkill] = []
            for skill_type in SkillStacks.SKILLS:
                base_class = globals()[skill_type]
                base: BaseSkill = base_class()

                if not base.droppable:
                    continue

                if level >= base.min_level and level <= base.max_level:
                    available.append(base)

            base_skill = random.choice(available)
        else:
            base_class = globals()[skill_type]
            base_skill: BaseSkill = base_class()

        additional_charges = max(1, int(base_skill.stacks * 0.3))

        rarity_map = {1: Rarity.COMMON}
        for rarity in self.RARITY_VALUE_SCALING:
            if self.MIN_RARITY_LVL[rarity] > level:
                continue
            value = int(additional_charges * self.RARITY_VALUE_SCALING[rarity])
            rarity_map[value] = rarity

        self.base_skill = base_skill
        self.skill_type = base_skill.skill_type
        self.value = additional_charges
        self.name = f"{self.base_skill.name} Charges"
        self.description = f"{self.base_skill.name} has additional charge(s)."
        self.special = self.skill_type.value
        self.image_url = self.base_skill.image_url

        self.rarities = rarity_map.values()
        self.custom_scaling = self.RARITY_VALUE_SCALING


class PhysDamageProc(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Bloody Murder",
            min_level=5,
            enchantment_type=EnchantmentType.PHYS_DAMAGE_PROC,
            description="Has a chance to deal additional physical damage on hit.",
            information="",
            slot=EquipmentSlot.WEAPON,
            stacks=20,
            droppable=True,
            value=0.75,
            proc_chance=0.5,
            cooldown=0,
            weight=20,
            skill_effect=SkillEffect.PHYSICAL_DAMAGE,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_ATTACK],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            emoji="💢",
        )


class MagDamageProc(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Overload",
            min_level=5,
            enchantment_type=EnchantmentType.MAG_DAMAGE_PROC,
            description="Has a chance to deal additional magical damage on hit.",
            information="",
            slot=EquipmentSlot.WEAPON,
            stacks=10,
            droppable=True,
            value=1.5,
            proc_chance=0.25,
            weight=20,
            skill_effect=SkillEffect.MAGICAL_DAMAGE,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_ATTACK],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            emoji="💫",
        )


class CleansingHeal(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Inner Peace",
            min_level=5,
            enchantment_type=EnchantmentType.CLEANSING_HEAL,
            description="Your heals are stronger and remove all negative status effects.",
            information="",
            slot=EquipmentSlot.ARMOR,
            stacks=5,
            droppable=True,
            value=10,
            cooldown=0,
            weight=15,
            value_type=ValueType.PERCENTAGE,
            skill_effect=SkillEffect.BUFF,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_ATTACK],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            emoji="🩹",
        )


class BallReset(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Bouncy Balls",
            min_level=4,
            enchantment_type=EnchantmentType.BALL_RESET,
            description="Your Ice and Fire Balls have a random chance to bounce back, resetting their cooldown immediately.",
            information="",
            slot=EquipmentSlot.WEAPON,
            stacks=10,
            droppable=True,
            value=10,
            cooldown=0,
            weight=15,
            value_type=ValueType.NONE,
            skill_effect=SkillEffect.CHANCE,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.POST_SKILL],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            emoji="🏐",
        )


class ExtraMissile(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Bigger Magazine",
            min_level=4,
            enchantment_type=EnchantmentType.EXTRA_MISSILE,
            description="With these bad boys your Magical and Physical Missile will fire one extra shot!",
            information="",
            slot=EquipmentSlot.WEAPON,
            stacks=10,
            droppable=True,
            value=1,
            weight=10,
            value_label="Missiles:",
            skill_effect=SkillEffect.NOTHING,
            value_type=ValueType.INT,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_ATTACK, EffectTrigger.SKILL_HITS],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            custom_value_scaling=self.NO_SCALING,
            emoji="",
        )


class ExtraGore(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Extra Gore",
            min_level=4,
            enchantment_type=EnchantmentType.EXTRA_GORE,
            description="Bleeds you inflict will apply an extra stack.",
            information="",
            slot=EquipmentSlot.WEAPON,
            stacks=10,
            droppable=True,
            value=1,
            weight=25,
            skill_effect=SkillEffect.NOTHING,
            value_label="Stacks",
            value_type=ValueType.INT,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_STATUS_APPLICATION],
            consumed=[EffectTrigger.ON_TRIGGER_SUCCESS],
            custom_value_scaling=self.NO_SCALING,
            emoji="🩸",
        )
