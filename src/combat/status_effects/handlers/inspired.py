from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    StatusEffectOutcome,
)
from combat.status_effects.status_effects import Inspired
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from control.controller import Controller


class InspiredHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Inspired()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        outcome = StatusEffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        if handler_context.skill.base_skill.skill_effect in [
            SkillEffect.BUFF,
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
        ]:
            return outcome

        outcome.modifier = 1 + (status_effect.event.value / 100)

        return outcome

    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        return self.combine_outcomes(outcomes)