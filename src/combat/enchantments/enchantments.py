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
            rarities=[Rarity.UNIQUE],
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
            rarities=[Rarity.UNIQUE],
            droppable=True,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Exalted(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Exalted Bean",
            enchantment_type=EnchantmentType.EXALTED,
            description=(
                "Adds a random modifier to the item and upgrades it to the next rarity. "
                "Only works on gear of the same rarity as this item."
            ),
            information="",
            rarities=[Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE],
            filter_flags=[EnchantmentFilterFlags.MATCH_RARITY],
            droppable=True,
            image_url="https://i.imgur.com/B6TuHg3.png",
        )


class Chance(BaseCraftingEnchantment):

    def __init__(self):
        super().__init__(
            name="Chance Bean",
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
            value=0.2,
            cooldown=2,
            skill_effect=SkillEffect.HEALING,
            image_url="https://i.imgur.com/B6TuHg3.png",
            trigger=[EffectTrigger.ON_DEATH],
            consumed=[EffectTrigger.ON_DEATH],
            emoji="",
        )
