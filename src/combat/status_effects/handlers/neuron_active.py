from combat.effects.efffect import EffectOutcome
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import NeuronActive
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from control.controller import Controller


class NeuronActiveHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=NeuronActive()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
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
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)
