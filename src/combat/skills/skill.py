import random

import discord

from combat.gear.droppable import Droppable, DroppableBase
from combat.gear.types import Base, EquipmentSlot, Rarity
from combat.skills.types import SkillEffect, SkillTarget, SkillType
from combat.status_effects.types import SkillStatusEffect
from config import Config
from control.types import FieldData
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


class BaseSkill(DroppableBase):

    DEFAULT_IMAGE = {
        SkillEffect.PHYSICAL_DAMAGE: "https://i.imgur.com/FHvWc7b.png",
        SkillEffect.NEUTRAL_DAMAGE: "https://i.imgur.com/FHvWc7b.png",
        SkillEffect.MAGICAL_DAMAGE: "https://i.imgur.com/zr785IX.png",
        SkillEffect.HEALING: "https://i.imgur.com/AH7NRhc.png",
    }

    def __init__(
        self,
        name: str,
        skill_type: SkillType,
        description: str,
        information: str,
        skill_effect: SkillEffect,
        cooldown: int,
        base_value: float,
        initial_cooldown: int = None,
        min_level: int = 1,
        max_level: int = 99,
        droppable: bool = True,
        hits: int = 1,
        stacks: int = None,
        status_effects: list[SkillStatusEffect] = None,
        reset_after_encounter: bool = False,
        aoe: bool = False,
        weight: int = 100,
        image_url: str = None,
        default_target: SkillTarget = SkillTarget.OPPONENT,
        modifiable: bool = True,
        max_targets: int = None,
        no_scaling: bool = False,
        custom_crit: float = None,
        uniques: list[SkillType] = None,
        base_skill_type: SkillType = None,
        author: str = None,
        max_hits: int = None,
        custom_value: float = None,
    ):
        super().__init__(
            name=name,
            base_type=Base.SKILL,
            slot=EquipmentSlot.SKILL,
            type=skill_type,
            min_level=min_level,
            max_level=max_level,
            weight=weight,
            droppable=droppable,
            uniques=uniques,
            author=author,
        )
        self.name = name
        self.skill_type = skill_type
        self.description = description
        self.information = information
        self.skill_effect = skill_effect
        self.cooldown = cooldown
        self.base_value = base_value
        self.initial_cooldown = initial_cooldown
        self.hits = hits
        self.stacks = stacks
        self.status_effects = status_effects
        self.reset_after_encounter = reset_after_encounter
        self.aoe = aoe
        self.modifiable = modifiable
        self.default_target = default_target
        self.image_url = image_url
        self.custom_crit = custom_crit
        self.max_targets = max_targets
        self.no_scaling = no_scaling
        self.max_hits = max_hits
        self.base_skill_type = base_skill_type
        self.custom_value = custom_value

        if self.image_url is None:
            self.image_url = self.DEFAULT_IMAGE[self.skill_effect]

        if self.status_effects is None:
            self.status_effects = []

        if self.base_skill_type is None:
            self.base_skill_type = self.skill_type


class Skill(Droppable, Forgeable):

    EFFECT_LABEL_MAP = {
        SkillEffect.NEUTRAL_DAMAGE: "Damage",
        SkillEffect.PHYSICAL_DAMAGE: "Damage",
        SkillEffect.MAGICAL_DAMAGE: "Damage",
        SkillEffect.NOTHING: "",
        SkillEffect.BUFF: "Effect",
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
        SkillEffect.PHYSICAL_DAMAGE: 0,
        SkillEffect.MAGICAL_DAMAGE: 1,
        SkillEffect.NEUTRAL_DAMAGE: 2,
        SkillEffect.EFFECT_DAMAGE: 3,
        SkillEffect.HEALING: 4,
        SkillEffect.BUFF: 5,
        SkillEffect.NOTHING: 6,
    }

    RARITY_STACKS_SCALING = {
        Rarity.DEFAULT: 1,
        Rarity.COMMON: 1,
        Rarity.UNCOMMON: 1.2,
        Rarity.RARE: 1.5,
        Rarity.LEGENDARY: 2,
        Rarity.UNIQUE: 1,
    }

    RARITY_DAMAGE_SCALING = {
        Rarity.DEFAULT: 0,
        Rarity.COMMON: 0,
        Rarity.UNCOMMON: 0.1,
        Rarity.RARE: 0.2,
        Rarity.LEGENDARY: 0.3,
        Rarity.UNIQUE: 0,
    }

    def __init__(
        self,
        base_skill: BaseSkill,
        rarity: Rarity,
        level: int,
        locked: bool = False,
        id: int = None,
    ):
        if not SkillType.is_weapon_skill(base_skill.skill_type):
            base_skill.base_value = base_skill.base_value * (
                1 + (self.RARITY_DAMAGE_SCALING[rarity] / base_skill.hits)
            )
        if base_skill.stacks is not None:
            base_skill.stacks = int(
                base_skill.stacks * self.RARITY_STACKS_SCALING[rarity]
            )

        Droppable.__init__(
            self,
            name=base_skill.name,
            base=base_skill,
            type=base_skill.skill_type,
            description=base_skill.description,
            information=base_skill.information,
            slot=EquipmentSlot.SKILL,
            level=level,
            rarity=rarity,
            base_value=base_skill.base_value,
            image_url=base_skill.image_url,
        )
        Forgeable.__init__(
            self,
            name=base_skill.name,
            id=id,
            object_type=ObjectType.SKILL,
            forge_type=base_skill.skill_type,
            value=base_skill.base_value,
            level=level,
            rarity=rarity,
            image_url=base_skill.image_url,
        )
        self.locked = locked
        self.base_skill = base_skill
        self.id = id

    def display(
        self,
        equipped: bool = False,
        scrap_value: int = None,
    ) -> ObjectDisplay:
        slot = self.base.slot.value
        if SkillType.is_weapon_skill(self.base_skill.skill_type):
            slot = "Weapon Skill"
        parameters = ObjectParameters(
            object_type=ObjectType.SKILL,
            name=self.name,
            group=slot,
            equipped=equipped,
            description=self.description,
            rarity=self.rarity,
            information=self.information,
        )

        prefixes: list[Prefix] = []
        suffixes: list[Suffix] = []

        suffixes.append(Suffix("Rarity", self.rarity.value, ValueType.STRING))

        # Base
        if self.scaling > 0:
            name = "Power"
            value_type = ValueType.FLOAT
            if self.base_skill.skill_effect == SkillEffect.BUFF:
                value_type = ValueType.PERCENTAGE
            prefixes.append(Prefix(name, self.scaling, value_type))

        # Hits
        if self.base_skill.hits > 1:
            name = "Hits"
            prefixes.append(Prefix(name, self.base_skill.hits, ValueType.INT))

        # Type
        name = "Type"
        prefixes.append(
            Prefix(name, self.base_skill.skill_effect.value, ValueType.STRING)
        )

        # Cooldown
        cooldown = self.base_skill.cooldown
        if cooldown is not None and cooldown > 0:
            name = "Cooldown"
            suffixes.append(Suffix(name, cooldown, ValueType.STRING, post=" Turn(s)"))

        # Stacks
        max_stacks = self.base_skill.stacks
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            if self.base_skill.reset_after_encounter:
                append = "(per Combat)"
            else:
                append = "(Total)"
            prefixes.append(Prefix(name, max_stacks, ValueType.STRING, post=append))

        extra_blocks: list[DisplayBlock] = []

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
        show_info: bool = False,
        equipped: bool = False,
        scrap_value: int = None,
    ) -> discord.Embed:
        display = self.display(
            equipped=equipped,
            scrap_value=scrap_value,
        )
        return display.get_embed(show_info)


class CharacterSkill:

    def __init__(
        self,
        skill: Skill,
        last_used: int,
        stacks_used: int,
        min_roll: int,
        max_roll: int,
        penalty: bool = False,
        additional_stacks: int = None,
        additional_hits: int = None,
    ):
        self.skill = skill
        self.last_used = last_used
        self.stacks_used = stacks_used
        self.min_roll = min_roll
        self.max_roll = max_roll
        self.penalty = penalty
        self.additional_stacks = additional_stacks
        self.additional_hits = additional_hits

    def on_cooldown(self):
        if self.last_used is None or self.skill.base_skill.cooldown is None:
            return False
        return self.last_used < self.skill.base_skill.cooldown

    def stacks_left(self):
        if self.max_stacks() is None or self.stacks_used is None:
            return None
        return self.max_stacks() - self.stacks_used

    def max_stacks(self):
        total = self.skill.base_skill.stacks
        if self.additional_stacks is not None:
            total += self.additional_stacks
        return total

    def hits(self):
        total = self.skill.base_skill.hits
        if self.additional_hits is not None:
            total += self.additional_hits
        return total

    def display(
        self,
        equipped: bool = False,
        amount: int = None,
    ) -> ObjectDisplay:
        base_display = self.skill.display(equipped=equipped)
        damage_prefix = None
        stacks_prefix = None

        # Damage
        caption = self.skill.EFFECT_LABEL_MAP[self.skill.base_skill.skill_effect]
        match self.skill.base_skill.skill_effect:
            case SkillEffect.BUFF:
                damage_prefix = Prefix(
                    caption, self.skill.base_skill.base_value, ValueType.PERCENTAGE
                )
            case _:
                damage_prefix = MultiPrefix(
                    caption,
                    values=[self.min_roll, self.max_roll],
                    value_separator=" - ",
                    value_type=ValueType.INT,
                    penalty=self.penalty,
                )

        # Stacks
        max_stacks = self.max_stacks()
        if max_stacks is not None and max_stacks > 0:
            name = "Uses"
            if self.skill.base_skill.reset_after_encounter:
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
        cooldown = self.skill.base_skill.cooldown
        if cooldown is not None and self.on_cooldown():
            cooldown_remaining = cooldown - self.last_used
            content = f"available in {ValueColor.PINK.value}{cooldown_remaining}{ValueColor.NONE.value} turn(s)"
            raw_content = f"available in {cooldown_remaining} turn(s)"
            extra_blocks = extra_blocks + [
                DisplayBlock(BlockType.ANSI, content, len(raw_content))
            ]

        if amount is not None and amount > 1:
            suffix = Suffix("Amount", amount, ValueType.INT)
            extra_blocks.append(
                AffixBlock([], [suffix], base_display.parameters.max_width)
            )

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
        equipped: bool = False,
        show_info: bool = False,
        amount: int = None,
    ) -> discord.Embed:
        display = self.display(
            equipped=equipped,
            amount=amount,
        )
        return display.get_embed(show_info)

    def add_to_embed(
        self,
        embed: discord.Embed,
        description_override: str = None,
    ) -> None:
        display = self.display()
        if description_override is not None:
            display.parameters.description = description_override

        embed.add_field(
            name="", value=display.get_embed_content(show_data=False), inline=False
        )

    def get_embed_field(
        self,
        max_width: int = None,
        description_override: str = None,
    ):
        if max_width is None:
            max_width = Config.COMBAT_EMBED_MAX_WIDTH

        prefix = ""
        if self.skill.rarity.value != Rarity.DEFAULT and not SkillType.is_weapon_skill(
            self.skill.base_skill.base_skill_type
        ):
            prefix = f"*{self.skill.rarity.value}* "

        title = f"> {prefix}**{self.skill.name}** "
        description = f'"{self.skill.description}"'
        if description_override is not None:
            description = f'"{description_override}"'

        if len(description) < max_width:
            description += " " + "\u00a0" * max_width

        info_block = f"```python\n{description}```"

        return FieldData(title, info_block, False)


class SkillInstance:

    def __init__(
        self,
        weapon_roll: int,
        skill_base: float,
        modifier: float,
        critical_modifier: float,
        encounter_scaling: float,
        crit_chance: float,
        is_crit: bool | None = None,
    ):
        self.weapon_roll = weapon_roll
        self.skill_base = skill_base
        self.modifier = modifier
        self.critical_modifier = critical_modifier
        self.encounter_scaling = encounter_scaling
        self.critical_chance = crit_chance
        self.is_crit = is_crit
        self.bonus_damage = None

    @property
    def value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        return int(value)

    @property
    def raw_value(self):
        value = self.weapon_roll * self.skill_base * self.modifier
        return int(value)

    @property
    def scaled_value(self):
        if self.is_crit is None:
            self.is_crit = random.random() < self.critical_chance

        value = self.weapon_roll * self.skill_base * self.modifier

        if self.is_crit:
            value *= self.critical_modifier

        if value > 0:
            value = max(1, value * self.encounter_scaling)

        return int(value)
