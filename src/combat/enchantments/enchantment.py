import random

import discord

from combat.effects.effect import Effect
from combat.effects.types import EffectTrigger
from combat.enchantments.types import (
    EnchantmentEffect,
    EnchantmentFilterFlags,
    EnchantmentType,
)
from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import Base, EquipmentSlot, Rarity
from combat.skills.types import SkillEffect
from forge.forgable import Forgeable
from view.object.embed import (
    AffixBlock,
    DisplayBlock,
    MultiPrefix,
    ObjectDisplay,
    ObjectParameters,
    Prefix,
    Suffix,
)
from view.object.types import BlockType, ObjectType, ValueColor, ValueType


class BaseEnchantment(DroppableBase):

    DEFAULT_IMAGE = {
        EnchantmentEffect.EFFECT: "https://i.imgur.com/FHvWc7b.png",
        EnchantmentEffect.CRAFTING: "https://i.imgur.com/FHvWc7b.png",
    }

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        enchantment_effect: EnchantmentEffect,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        weight: int = 100,
        rarities: list[Rarity] = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        author: str = None,
        filter_flags: list[EnchantmentFilterFlags] = None,
        special: str | None = None,
        value_label: str | None = None,
        custom_value_scaling: dict[Rarity, float] | None = None,
        custom_stack_scaling: dict[Rarity, float] | None = None,
        value_type: ValueType = ValueType.FLOAT,
    ):
        super().__init__(
            name=name,
            base_type=Base.ENCHANTMENT,
            slot=slot,
            type=enchantment_type,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
            uniques=uniques,
            author=author,
        )
        self.filter_flags = filter_flags
        self.name = name
        self.value = value
        self.enchantment_type = enchantment_type
        self.description = description
        self.information = information
        self.enchantment_effect = enchantment_effect
        self.image_url = image_url
        self.base_enchantment_type = base_enchantment_type
        self.rarities = rarities
        self.special = special
        self.value_label = value_label
        self.custom_value_scaling = custom_value_scaling
        self.custom_stack_scaling = custom_stack_scaling
        self.value_type = value_type

        if self.rarities is None:
            self.rarities = [
                Rarity.COMMON,
                Rarity.UNCOMMON,
                Rarity.RARE,
                Rarity.LEGENDARY,
            ]

        if self.filter_flags is None:
            self.filter_flags = []

        if self.image_url is None:
            self.image_url = self.DEFAULT_IMAGE[self.enchantment_effect]

        if self.base_enchantment_type is None:
            self.base_enchantment_type = self.enchantment_type


class BaseCraftingEnchantment(BaseEnchantment):

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        weight: int = 100,
        rarities: list[Rarity] = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        filter_flags: list[EnchantmentFilterFlags] = None,
        value_label: str | None = None,
        custom_value_scaling: str | None = None,
        custom_stack_scaling: str | None = None,
        author: str = None,
    ):
        super().__init__(
            name=name,
            enchantment_type=enchantment_type,
            description=description,
            information=information,
            enchantment_effect=EnchantmentEffect.CRAFTING,
            value=value,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            droppable=droppable,
            weight=weight,
            rarities=rarities,
            image_url=image_url,
            uniques=uniques,
            base_enchantment_type=base_enchantment_type,
            filter_flags=filter_flags,
            value_label=value_label,
            custom_value_scaling=custom_value_scaling,
            custom_stack_scaling=custom_stack_scaling,
            author=author,
        )


class BaseEffectEnchantment(BaseEnchantment, Effect):

    NO_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1,
        Rarity.RARE: 1,
        Rarity.LEGENDARY: 1,
    }

    def __init__(
        self,
        name: str,
        enchantment_type: EnchantmentType,
        description: str,
        information: str,
        value: float = 0,
        slot: EquipmentSlot = EquipmentSlot.ANY,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        stacks: int = None,
        hits: int = 1,
        proc_chance: float = 1,
        cooldown: int = None,
        initial_cooldown: int = None,
        reset_after_encounter: bool = False,
        weight: int = 100,
        rarities: list[Rarity] = None,
        image_url: str = None,
        uniques: list[EnchantmentType] = None,
        base_enchantment_type: EnchantmentType = None,
        author: str = None,
        trigger: list[EffectTrigger] = None,
        consumed: list[EffectTrigger] = None,
        skill_effect: SkillEffect = None,
        emoji: str = None,
        delay_trigger: bool = False,
        delay_consume: bool = False,
        delay_for_source_only: bool = False,
        filter_flags: list[EnchantmentFilterFlags] = None,
        single_description: bool = False,
        value_type: ValueType = ValueType.FLOAT,
        value_label: str | None = None,
        custom_value_scaling: str | None = None,
        custom_stack_scaling: str | None = None,
    ):
        if filter_flags is None:
            filter_flags = [EnchantmentFilterFlags.LESS_OR_EQUAL_RARITY]
        BaseEnchantment.__init__(
            self,
            name=name,
            enchantment_type=enchantment_type,
            description=description,
            information=information,
            enchantment_effect=EnchantmentEffect.EFFECT,
            value=value,
            slot=slot,
            min_level=min_level,
            max_level=max_level,
            droppable=droppable,
            weight=weight,
            rarities=rarities,
            image_url=image_url,
            uniques=uniques,
            base_enchantment_type=base_enchantment_type,
            filter_flags=filter_flags,
            value_label=value_label,
            custom_value_scaling=custom_value_scaling,
            custom_stack_scaling=custom_stack_scaling,
            value_type=value_type,
            author=author,
        )
        Effect.__init__(
            self,
            effect_type=enchantment_type,
            name=name,
            description=description,
            trigger=trigger,
            consumed=consumed,
            skill_effect=skill_effect,
            emoji=emoji,
            delay_trigger=delay_trigger,
            delay_consume=delay_consume,
            delay_for_source_only=delay_for_source_only,
            single_description=single_description,
        )
        self.stacks = stacks
        self.cooldown = cooldown
        self.proc_chance = proc_chance
        self.initial_cooldown = initial_cooldown
        self.reset_after_encounter = reset_after_encounter
        self.hits = hits


class Enchantment(Droppable, Forgeable):

    TYPE_LABEL_MAP = {
        EnchantmentEffect.CRAFTING: "Crafting",
        EnchantmentEffect.EFFECT: "Gear Effect",
    }

    EFFECT_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Damage",
        SkillEffect.PHYSICAL_DAMAGE: "Damage",
        SkillEffect.MAGICAL_DAMAGE: "Damage",
        SkillEffect.EFFECT_DAMAGE: "Damage",
        SkillEffect.NOTHING: "",
        SkillEffect.BUFF: "Buff",
        SkillEffect.CHANCE: "Chance",
        SkillEffect.HEALING: "Healing",
    }

    EFFECT_TYPE_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Neutral Dmg.",
        SkillEffect.PHYSICAL_DAMAGE: "Phys. Dmg.",
        SkillEffect.MAGICAL_DAMAGE: "Mag. Dmg.",
        SkillEffect.EFFECT_DAMAGE: "Neutral Dmg.",
        SkillEffect.NOTHING: "Special",
        SkillEffect.BUFF: "Buff",
        SkillEffect.CHANCE: "Special",
        SkillEffect.HEALING: "Healing",
    }

    RARITY_SORT_MAP = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 2,
        Rarity.RARE: 3,
        Rarity.LEGENDARY: 4,
        Rarity.UNIQUE: 5,
    }

    EFFECT_SORT_MAP = {
        EnchantmentEffect.CRAFTING: 0,
        EnchantmentEffect.EFFECT: 1,
    }

    RARITY_STACKS_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.2,
        Rarity.RARE: 1.5,
        Rarity.LEGENDARY: 2,
        Rarity.UNIQUE: 1,
    }

    RARITY_VALUE_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.1,
        Rarity.RARE: 1.2,
        Rarity.LEGENDARY: 1.3,
        Rarity.UNIQUE: 1,
    }

    def __init__(
        self,
        base_enchantment: BaseEnchantment,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        id: int = None,
    ):
        if base_enchantment.custom_value_scaling is None:
            base_enchantment.value *= self.RARITY_VALUE_SCALING[rarity]
        else:
            base_enchantment.value *= base_enchantment.custom_value_scaling[rarity]

        if base_enchantment.value_type == ValueType.INT:
            base_enchantment.value = int(base_enchantment.value)

        Droppable.__init__(
            self,
            name=base_enchantment.name,
            base=base_enchantment,
            type=base_enchantment.enchantment_type,
            description=base_enchantment.description,
            information=base_enchantment.information,
            slot=base_enchantment.slot,
            level=level,
            rarity=rarity,
            base_value=base_enchantment.value,
            image_url=base_enchantment.image_url,
        )
        Forgeable.__init__(
            self,
            name=base_enchantment.name,
            id=id,
            object_type=ObjectType.ENCHANTMENT,
            forge_type=base_enchantment.enchantment_type,
            value=base_enchantment.value,
            level=level,
            rarity=rarity,
            image_url=base_enchantment.image_url,
        )
        self.locked = locked
        self.base_enchantment = base_enchantment
        self.id = id

    def display(
        self,
        scrap_value: int = None,
        amount: int = None,
    ) -> ObjectDisplay:
        parameters = ObjectParameters(
            object_type=ObjectType.ENCHANTMENT,
            name=self.name,
            group="Enchantment",
            description=self.description,
            rarity=self.rarity,
            information=self.information,
        )

        prefixes: list[Prefix] = []
        suffixes: list[Suffix] = []

        suffixes.append(Suffix("Rarity", self.rarity.value, ValueType.STRING))

        name = "Type"
        type_value = self.TYPE_LABEL_MAP[self.base_enchantment.enchantment_effect.value]
        prefixes.append(Prefix(name, type_value, ValueType.STRING))

        value = self.base_enchantment.value
        if value > 0:
            name = "Value"
            if self.base_enchantment.value_label is not None:
                name = self.base_enchantment.value_label

            prefixes.append(Prefix(name, value, self.base_enchantment.value_type))

        extra_blocks: list[DisplayBlock] = []

        if amount is not None and amount > 1:
            suffix = Suffix("Amount", amount, ValueType.INT)
            extra_blocks.append(AffixBlock([], [suffix], parameters.max_width))

        if scrap_value is not None:
            prefix = Prefix("Stock", 1, ValueType.INT)
            suffix = Suffix("Cost", f"⚙️{scrap_value}", ValueType.STRING)
            extra_blocks.append(AffixBlock([prefix], [suffix], parameters.max_width))

        return ObjectDisplay(
            parameters=parameters,
            prefixes=prefixes,
            suffixes=suffixes,
            extra_blocks=extra_blocks,
            thumbnail_url=self.image_url,
            author=self.base.author,
        )

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        display = self.display(
            scrap_value=scrap_value,
            amount=amount,
        )
        return display.get_embed(show_info)

    def get_info_text(self, cooldown: int = None, uses: tuple[int, int] = None):

        name = f"<~ {self.name} ~>"
        color = f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}"

        if uses is not None and uses[0] <= 0:
            color = "[30m"

            info_block = f"{color}{name}"
            info_block += f" [{uses[0]}/{uses[1]}]"
            info_block += "[0m"
            return info_block
        else:
            color = f"{Droppable.RARITY_NAME_COLOR_MAP[self.rarity]}"
            info_block = f"{color}{name}"
            info_block += "[0m"

        if uses is not None:
            info_block += f" [{uses[0]}/{uses[1]}]"

        if cooldown is not None and cooldown > 0:
            info_block += f" (in {cooldown} turns)"

        return info_block


class EffectEnchantment(Enchantment):

    def __init__(
        self,
        base_enchantment: BaseEffectEnchantment,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        priority: int = 100,
        id: int = None,
    ):
        super().__init__(
            base_enchantment=base_enchantment,
            rarity=rarity,
            level=level,
            locked=locked,
            id=id,
        )

        if base_enchantment.stacks is not None:
            if base_enchantment.custom_stack_scaling is not None:
                base_enchantment.stacks = int(
                    base_enchantment.stacks
                    * base_enchantment.custom_stack_scaling[rarity]
                )
            else:
                base_enchantment.stacks = int(
                    base_enchantment.stacks * self.RARITY_STACKS_SCALING[rarity]
                )

        self.base_enchantment: BaseEffectEnchantment = base_enchantment
        self.priority = priority

    def display(
        self,
        scrap_value: int = None,
        amount: int = None,
    ) -> ObjectDisplay:
        parameters = ObjectParameters(
            object_type=ObjectType.ENCHANTMENT,
            name=self.name,
            group="Enchantment",
            description=self.description,
            rarity=self.rarity,
            information=self.information,
        )

        prefixes: list[Prefix] = []
        suffixes: list[Suffix] = []

        suffixes.append(Suffix("Rarity", self.rarity.value, ValueType.STRING))

        # Base Value
        if self.scaling > 0:
            name = "Power"
            if self.base_enchantment.value_label is not None:
                name = self.base_enchantment.value_label

            prefixes.append(
                Prefix(name, self.scaling, self.base_enchantment.value_type)
            )

        # Hits
        if self.base_enchantment.hits > 1:
            prefixes.append(Prefix(name, self.base_enchantment.hits, ValueType.INT))

        # Type
        name = "Type"
        type_value = self.TYPE_LABEL_MAP[self.base_enchantment.enchantment_effect.value]
        prefixes.append(Prefix(name, type_value, ValueType.STRING))

        if self.base_enchantment.skill_effect is not None:
            # Type
            name = "Effect"
            effect_value = self.EFFECT_TYPE_LABEL_MAP[
                self.base_enchantment.skill_effect.value
            ]
            prefixes.append(Prefix(name, effect_value, ValueType.STRING))

        # Slot
        name = "Slot"
        suffixes.append(
            Suffix(name, self.base_enchantment.slot.value, ValueType.STRING)
        )

        # Proc
        proc_chance = self.base_enchantment.proc_chance
        if proc_chance is not None and proc_chance < 1:
            name = "Chance"
            prefixes.append(Prefix(name, proc_chance, ValueType.PERCENTAGE))

        # Cooldown
        cooldown = self.base_enchantment.cooldown
        if cooldown is not None and cooldown > 0:
            name = "Cooldown"
            suffixes.append(Suffix(name, cooldown, ValueType.STRING, post=" Turn(s)"))

        # Stacks
        max_stacks = self.base_enchantment.stacks
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            if self.base_enchantment.reset_after_encounter:
                append = " (per Combat)"
            else:
                append = " (Total)"
            prefixes.append(Prefix(name, max_stacks, ValueType.STRING, post=append))

        extra_blocks: list[DisplayBlock] = []

        if amount is not None and amount > 1:
            suffix = Suffix("Amount", amount, ValueType.INT)
            extra_blocks.append(AffixBlock([], [suffix], parameters.max_width))

        if scrap_value is not None:
            prefix = Prefix("Stock", 1, ValueType.INT)
            suffix = Suffix("Cost", f"⚙️{scrap_value}", ValueType.STRING)
            extra_blocks.append(AffixBlock([prefix], [suffix], parameters.max_width))

        return ObjectDisplay(
            parameters=parameters,
            prefixes=prefixes,
            suffixes=suffixes,
            extra_blocks=extra_blocks,
            thumbnail_url=self.image_url,
            author=self.base.author,
        )

    def get_embed(
        self,
        show_data: bool = True,
        show_info: bool = False,
        show_locked_state: bool = False,
        scrap_value: int = None,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        display = self.display(
            scrap_value=scrap_value,
            amount=amount,
        )
        return display.get_embed(show_info)


class GearEnchantment:

    def __init__(
        self,
        enchantment: EffectEnchantment,
        last_used: int,
        stacks_used: int,
        min_roll: int,
        max_roll: int,
        penalty: bool = False,
    ):
        self.enchantment = enchantment
        self.last_used = last_used
        self.stacks_used = stacks_used
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.penalty = penalty

    def on_cooldown(self):
        if self.last_used is None or self.enchantment.base_enchantment.cooldown is None:
            return False
        return self.last_used <= self.enchantment.base_enchantment.cooldown

    def proc(self):
        chance = self.enchantment.base_enchantment.proc_chance
        if chance is None or chance == 1:
            return True
        return random.random() < chance

    def stacks_left(self):
        if self.enchantment.base_enchantment.stacks is None or self.stacks_used is None:
            return None
        return self.enchantment.base_enchantment.stacks - self.stacks_used

    def display(
        self,
        scrap_value: int = None,
        amount: int = None,
    ) -> ObjectDisplay:

        base_display = self.enchantment.display(scrap_value, amount)
        damage_prefix = None
        stacks_prefix = None

        # Damage
        if self.enchantment.base_enchantment.value > 0:
            caption = self.enchantment.EFFECT_LABEL_MAP[
                self.enchantment.base_enchantment.skill_effect
            ]
            if self.enchantment.base_enchantment.value_label is not None:
                caption = self.enchantment.base_enchantment.value_label

            value_type = self.enchantment.base_enchantment.value_type

            if self.enchantment.base_enchantment.skill_effect not in [
                SkillEffect.BUFF,
                SkillEffect.CHANCE,
                SkillEffect.NOTHING,
            ]:
                damage_prefix = MultiPrefix(
                    caption,
                    values=[self.min_roll, self.max_roll],
                    value_separator=" - ",
                    value_type=ValueType.INT,
                    penalty=self.penalty,
                )
            else:
                damage_prefix = Prefix(
                    caption, self.enchantment.base_enchantment.value, value_type
                )

        # Stacks
        max_stacks = self.enchantment.base_enchantment.stacks
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            if self.enchantment.base_enchantment.reset_after_encounter:
                append = " (per Combat)"
            else:
                append = " (Total)"

            stacks_prefix = MultiPrefix(
                name,
                values=[self.stacks_left(), max_stacks],
                value_separator="/",
                post=append,
                value_type=ValueType.INT,
            )

        new_prefixes = []

        for prefix in base_display.prefixes:
            if damage_prefix is not None and prefix.name in ["Power", caption]:
                new_prefixes.append(damage_prefix)
                continue
            if stacks_prefix is not None and prefix.name == stacks_prefix.name:
                new_prefixes.append(stacks_prefix)
                continue
            new_prefixes.append(prefix)

        extra_blocks = base_display.extra_blocks
        cooldown = self.enchantment.base_enchantment.cooldown
        if cooldown is not None and self.on_cooldown():
            cooldown_remaining = cooldown - self.last_used
            content = f"available in {ValueColor.PINK.value}{cooldown_remaining}{ValueColor.NONE.value} turn(s)"
            raw_content = f"available in {cooldown_remaining} turn(s)"
            extra_blocks = extra_blocks + [
                DisplayBlock(BlockType.ANSI, content, len(raw_content))
            ]

        return ObjectDisplay(
            parameters=base_display.parameters,
            prefixes=new_prefixes,
            suffixes=base_display.suffixes,
            extra_blocks=extra_blocks,
            thumbnail_url=base_display.thumbnail_url,
            author=base_display.author,
        )

    def get_embed(
        self,
        show_info: bool = False,
        amount: int = None,
    ) -> discord.Embed:
        display = self.display(
            amount=amount,
        )
        return display.get_embed(show_info)


class CraftDisplayWrapper(GearEnchantment):

    def __init__(
        self,
        enchantment: Enchantment,
    ):
        super().__init__(
            enchantment=enchantment,
            last_used=0,
            stacks_used=0,
            min_roll=0,
            max_roll=0,
            penalty=False,
        )

    def get_embed(
        self,
        show_data: bool = True,
        show_full_data: bool = False,
        show_info: bool = False,
        show_locked_state: bool = False,
        amount: int = None,
        max_width: int = None,
    ) -> discord.Embed:
        return self.enchantment.get_embed(
            show_data=show_data,
            show_info=show_info,
            show_locked_state=show_locked_state,
            amount=amount,
            max_width=max_width,
        )
