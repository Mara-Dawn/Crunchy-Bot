from combat.effects.efffect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    OutcomeFlag,
)
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
)
from combat.status_effects.status_effects import StatusImmune
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from control.controller import Controller


class StatusImmuneHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=StatusImmune()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        if StatusEffectType.is_negative(handler_context.triggering_status_effect_type):
            outcome.flags = [OutcomeFlag.PREVENT_STATUS_APPLICATION]
            triggering_status_effect = await self.factory.get_status_effect(
                handler_context.triggering_status_effect_type
            )
            info = f"{triggering_status_effect.name} could not be applied."

            embed_data_collection = EmbedDataCollection()
            description = info
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
