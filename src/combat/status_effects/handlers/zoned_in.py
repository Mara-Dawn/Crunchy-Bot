from combat.effects.effect import EffectOutcome
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import ZonedIn
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller


class ZonedInHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=ZonedIn()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        outcome.crit_chance = 1

        return outcome

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)
