from dataclasses import dataclass
from enum import Enum
from typing import Any

from combat.effects.types import EffectTrigger
from combat.enchantments.types import EnchantmentType
from combat.skills.skill import SkillInstance
from combat.skills.types import SkillEffect
from combat.status_effects.types import StatusEffectType


class Effect:

    def __init__(
        self,
        effect_type: StatusEffectType | EnchantmentType,
        name: str,
        description: str,
        trigger: list[EffectTrigger],
        consumed: list[EffectTrigger],
        skill_effect: SkillEffect = None,
        emoji: str = None,
        delay_trigger: bool = False,
        delay_consume: bool = False,
        delay_for_source_only: bool = False,
        single_description: bool = False,
    ):
        self.effect_type = effect_type
        self.name = name
        self.description = description
        self.skill_effect = skill_effect
        self.trigger = trigger
        self.consumed = consumed
        self.emoji = emoji
        self.delay_trigger = delay_trigger
        self.delay_consume = delay_consume
        self.delay_for_source_only = delay_for_source_only
        self.single_description = single_description
        self.title = f"{self.emoji} {self.name}"

        if self.skill_effect is None:
            self.skill_effect = SkillEffect.EFFECT_DAMAGE


class OutcomeFlag(Enum):
    PREVENT_STATUS_APPLICATION = 1
    PREVENT_DEATH = 2
    NO_CONSUME = 3
    ADDITIONAL_STACK_VALUE = 4


@dataclass
class EffectEmbedData:
    effect: Effect
    title: str
    description: str

    @property
    def effect_type(self):
        return self.effect.effect_type

    def append(self, description: str):
        if not self.effect.single_description:
            self.description += f"\n{description}"


@dataclass
class EmbedDataCollection:
    _embed_data: dict[StatusEffectType | EnchantmentType, EffectEmbedData] = None

    @property
    def embed_data(self):
        if self._embed_data is None:
            self._embed_data = {}
        return self._embed_data

    @property
    def length(self):
        return len(self.embed_data)

    def values(self):
        return self.embed_data.values()

    def append(self, embed_data: EffectEmbedData):
        if embed_data.effect_type not in self.embed_data:
            self.embed_data[embed_data.effect_type] = embed_data
        else:
            self.embed_data[embed_data.effect_type].append(embed_data.description)

    def extend(self, collection: "EmbedDataCollection"):
        for embed_data in collection.values():
            self.append(embed_data)


@dataclass
class EffectOutcome:
    value: Any | None = None
    modifier: float | None = None
    crit_chance: float | None = None
    crit_chance_modifier: float | None = None
    initiative: int | None = None
    applied_effects: list[tuple[StatusEffectType, int]] | None = None
    flags: list[OutcomeFlag] | None = None
    info: str | None = None
    bonus_damage: int | None = None
    embed_data: EmbedDataCollection | None = None

    @staticmethod
    def EMPTY():
        return EffectOutcome()

    def apply_to_instance(self, instance: SkillInstance):
        if self.modifier is not None:
            instance.modifier *= self.modifier
        if self.bonus_damage is not None:
            instance.bonus_damage = self.bonus_damage
        if instance.is_crit is None:
            if self.crit_chance is not None:
                instance.critical_chance = self.crit_chance
            if self.crit_chance_modifier is not None:
                instance.critical_chance *= self.crit_chance_modifier
