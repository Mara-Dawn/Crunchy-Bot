import random

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    HandlerContext,
)
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import High
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller


class HighHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=High())

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        outcome.modifier = 0.5 + random.random()

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.target.name} is blazed out of their mind causing unexpected skill outcomes."
        embed_data = EffectEmbedData(
            self.status_effect, self.status_effect.title, description
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection

        return outcome

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)
