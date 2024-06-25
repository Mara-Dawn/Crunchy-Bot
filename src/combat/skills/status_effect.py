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
        priority: int = 100,
        damage_type: SkillEffect = None,
        max_stacks: int = MAX_STACKS,
        display_status: bool = False,
        emoji: str = None,
    ):
        self.effect_type = effect_type
        self.name = name
        self.description = description
        self.priority = priority
        self.damage_type = damage_type
        self.trigger = trigger
        self.max_stacks = max_stacks
        self.emoji = emoji
        self.display_status = display_status

        if self.damage_type is None:
            self.damage_type = SkillEffect.STATUS_EFFECT_DAMAGE


class SkillStatusEffect:

    def __init__(
        self,
        status_effect_type: StatusEffectType,
        stacks: int,
        application: StatusEffectApplication = StatusEffectApplication.DEFAULT,
    ):
        self.status_effect_type = status_effect_type
        self.stacks = stacks
        self.application = application


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
