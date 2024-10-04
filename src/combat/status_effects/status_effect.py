from dataclasses import dataclass
from enum import Enum
from typing import Any

from combat.skills.skill import SkillInstance
from combat.skills.types import SkillEffect
from combat.status_effects.types import (
    StatusEffectTrigger,
    StatusEffectType,
)
from events.status_effect_event import StatusEffectEvent


class StatusEffect:

    MAX_STACKS = 25

    def __init__(
        self,
        effect_type: StatusEffectType,
        name: str,
        description: str,
        trigger: list[StatusEffectTrigger],
        consumed: list[StatusEffectTrigger],
        priority: int = 100,
        damage_type: SkillEffect = None,
        max_stacks: int = MAX_STACKS,
        override_by_actor: bool = False,
        override: bool = False,
        stack: bool = False,
        display_status: bool = False,
        apply_on_miss: bool = False,
        emoji: str = None,
        delay_trigger: bool = False,
        delay_consume: bool = False,
        delay_for_source_only: bool = False,
        single_description: bool = False,
    ):
        self.effect_type = effect_type
        self.name = name
        self.description = description
        self.priority = priority
        self.damage_type = damage_type
        self.trigger = trigger
        self.consumed = consumed
        self.max_stacks = max_stacks
        self.emoji = emoji
        self.display_status = display_status
        self.override = override
        self.override_by_actor = override_by_actor
        self.stack = stack
        self.apply_on_miss = apply_on_miss
        self.delay_trigger = delay_trigger
        self.delay_consume = delay_consume
        self.delay_for_source_only = delay_for_source_only
        self.single_description = single_description
        self.title = f"{self.emoji} {self.name}"

        if self.damage_type is None:
            self.damage_type = SkillEffect.STATUS_EFFECT_DAMAGE


class OutcomeFlag(Enum):
    PREVENT_STATUS_APPLICATION = 1


class ActiveStatusEffect:

    def __init__(
        self,
        status_effect: StatusEffect,
        event: StatusEffectEvent,
        remaining_stacks: int,
    ):
        self.status_effect = status_effect
        self.event = event
        self.remaining_stacks = remaining_stacks


@dataclass
class StatusEffectEmbedData:
    status_effect: StatusEffect
    title: str
    description: str

    @property
    def effect_type(self):
        return self.status_effect.effect_type

    def append(self, description: str):
        if not self.status_effect.single_description:
            self.description += f"\n{description}"


@dataclass
class EmbedDataCollection:
    _embed_data: dict[StatusEffectType, StatusEffectEmbedData] = None

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

    def append(self, embed_data: StatusEffectEmbedData):
        if embed_data.effect_type not in self.embed_data:
            self.embed_data[embed_data.effect_type] = embed_data
        else:
            self.embed_data[embed_data.effect_type].append(embed_data.description)

    def extend(self, collection: "EmbedDataCollection"):
        for embed_data in collection.values():
            self.append(embed_data)


@dataclass
class StatusEffectOutcome:
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
        return StatusEffectOutcome()

    def apply_to_instance(self, instance: SkillInstance):
        if self.modifier is not None:
            instance.modifier *= self.modifier
        if instance.is_crit is None:
            if self.crit_chance is not None:
                instance.critical_chance = self.crit_chance
            if self.crit_chance_modifier is not None:
                instance.critical_chance *= self.crit_chance_modifier