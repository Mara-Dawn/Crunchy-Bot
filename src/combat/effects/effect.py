from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from combat.actors import Actor
from combat.effects.types import EffectTrigger
from combat.enchantments.types import EnchantmentType
from combat.encounter import EncounterContext
from combat.skills.skill import Skill, SkillInstance
from combat.skills.types import SkillEffect
from combat.status_effects.types import StatusEffectType
from control.controller import Controller


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
    embed_data: EmbedDataCollection | None = None

    @staticmethod
    def EMPTY():
        return EffectOutcome()

    def apply_to_instance(self, instance: SkillInstance):
        if self.modifier is not None:
            instance.modifier *= self.modifier
        if instance.is_crit is None:
            if self.crit_chance is not None:
                instance.critical_chance = self.crit_chance
            if self.crit_chance_modifier is not None:
                instance.critical_chance *= self.crit_chance_modifier


@dataclass
class HandlerContext:
    trigger: EffectTrigger = None
    context: EncounterContext = None
    source: Actor = None
    target: Actor = None
    skill: Skill = None
    trigger_value: float = None
    damage_instance: SkillInstance = None


class EffectHandler(ABC):

    def __init__(self, controller: Controller):
        self.controller = controller

    @abstractmethod
    async def handle(self) -> EffectOutcome:
        pass

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)

    @staticmethod
    def combine_outcomes(
        outcomes: list[EffectOutcome],
    ) -> EffectOutcome:
        combined = EffectOutcome.EMPTY()

        for outcome in outcomes:
            if outcome.value is not None and isinstance(outcome.value, int | float):
                if combined.value is None:
                    combined.value = outcome.value
                else:
                    combined.value += outcome.value

            if outcome.modifier is not None:
                if combined.modifier is None:
                    combined.modifier = outcome.modifier
                else:
                    combined.modifier *= outcome.modifier

            if outcome.crit_chance is not None:  # noqa: SIM102
                if (
                    combined.crit_chance is None
                    or combined.crit_chance < outcome.crit_chance
                ):
                    combined.crit_chance = outcome.crit_chance

            if outcome.crit_chance_modifier is not None:
                if combined.crit_chance_modifier is None:
                    combined.crit_chance_modifier = outcome.crit_chance_modifier
                else:
                    combined.crit_chance_modifier *= outcome.crit_chance_modifier

            if outcome.initiative is not None:
                if combined.initiative is None:
                    combined.initiative = outcome.initiative
                else:
                    combined.initiative += outcome.initiative

            if outcome.applied_effects is not None:
                if combined.applied_effects is None:
                    combined.applied_effects = outcome.applied_effects
                else:
                    combined.applied_effects.extend(outcome.applied_effects)

            if outcome.flags is not None:
                if combined.flags is None:
                    combined.flags = outcome.flags
                else:
                    combined.flags.extend(outcome.flags)

            if outcome.info is not None:
                if combined.info is None:
                    combined.info = outcome.info
                else:
                    combined.info += "\n" + outcome.info

            if outcome.embed_data is not None:
                if combined.embed_data is None:
                    combined.embed_data = outcome.embed_data
                else:
                    combined.embed_data.extend(outcome.embed_data)

        return combined
