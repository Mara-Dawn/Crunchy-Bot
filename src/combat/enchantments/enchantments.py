from combat.effects.types import EffectTrigger
from combat.enchantments.enchantment import (
    BaseCraftingEnchantment,
    BaseEffectEnchantment,
    BaseEnchantment,
)
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.gear.types import EquipmentSlot, Rarity
from combat.skills.types import SkillEffect

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
            enchantment_type=EnchantmentType.CHAOS,
            description="Randomly rerolls all modifiers on a gear piece of any rarity.",
            information="",
            fixed_rarity=Rarity.UNIQUE,
            droppable=True,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Divine(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Divine Bean",
            enchantment_type=EnchantmentType.DIVINE,
            description=(
                "Rerolls all modifier values on a gear piece of any rarity. "
                "The modifiers themselves will stay the same."
            ),
            information="",
            fixed_rarity=Rarity.UNIQUE,
            droppable=True,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


# Effect Enchantments


class DeathSave(BaseEffectEnchantment):

    def __init__(self):
        super().__init__(
            name="Cheat Death",
            enchantment_type=EnchantmentType.DEATH_SAVE,
            description="Allows you to survive lethal damage.",
            information="",
            slot=EquipmentSlot.ACCESSORY,
            stacks=1,
            droppable=True,
            skill_effect=SkillEffect.NOTHING,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_DEATH],
            consumed=[EffectTrigger.ON_DEATH],
            emoji="",
        )
