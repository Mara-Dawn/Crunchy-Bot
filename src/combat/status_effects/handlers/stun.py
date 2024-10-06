import datetime

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    HandlerContext,
)
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Stun
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class StunHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Stun())

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        event = EncounterEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            handler_context.target.id,
            EncounterEventType.FORCE_SKIP,
        )
        await self.controller.dispatch_event(event)

        embed_data_collection = EmbedDataCollection()
        description = "You are stunned."
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
