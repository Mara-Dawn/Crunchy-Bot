from combat.effects.effect import Effect
from combat.effects.types import EffectTrigger
from combat.skills.types import SkillEffect
from combat.status_effects.types import StatusEffectType
from events.status_effect_event import StatusEffectEvent


class StatusEffect(Effect):

    MAX_STACKS = 25

    def __init__(
        self,
        effect_type: StatusEffectType,
        name: str,
        description: str,
        trigger: list[EffectTrigger],
        consumed: list[EffectTrigger],
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
        super().__init__(
            effect_type=effect_type,
            name=name,
            description=description,
            trigger=trigger,
            consumed=consumed,
            skill_effect=damage_type,
            emoji=emoji,
            delay_trigger=delay_trigger,
            delay_consume=delay_consume,
            delay_for_source_only=delay_for_source_only,
            single_description=single_description,
        )
        self.priority = priority
        self.max_stacks = max_stacks
        self.display_status = display_status
        self.override = override
        self.override_by_actor = override_by_actor
        self.stack = stack
        self.apply_on_miss = apply_on_miss


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
