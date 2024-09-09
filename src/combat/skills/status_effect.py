from combat.skills.types import (
    SkillEffect,
    StatusEffectApplication,
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
        delay: bool = False,
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
        self.delay = delay

        if self.damage_type is None:
            self.damage_type = SkillEffect.STATUS_EFFECT_DAMAGE


class SkillStatusEffect:

    def __init__(
        self,
        status_effect_type: StatusEffectType,
        stacks: int,
        application: StatusEffectApplication = StatusEffectApplication.DEFAULT,
        application_value: float = None,
        application_chance: float = 1,
        self_target: bool = False,
    ):
        self.status_effect_type = status_effect_type
        self.stacks = stacks
        self.application = application
        self.application_value = application_value
        self.application_chance = application_chance
        self.self_target = self_target


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
