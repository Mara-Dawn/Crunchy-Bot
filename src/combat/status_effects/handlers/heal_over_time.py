import datetime

from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    EmbedDataCollection,
    StatusEffectEmbedData,
    StatusEffectOutcome,
)
from combat.status_effects.status_effects import HealOverTime
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class HealOverTimeHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=HealOverTime()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        outcome = StatusEffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        healing = int(status_effect.event.value)
        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            status_effect.event.source_id,
            status_effect.event.actor_id,
            status_effect.event.status_type,
            healing,
            healing,
            status_effect.event.id,
            CombatEventType.STATUS_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        outcome.value = healing

        return outcome

    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        combined = self.combine_outcomes(outcomes)

        if combined.value is not None:
            embed_data_collection = EmbedDataCollection()
            description = (
                f"{handler_context.target.name} heals for {combined.value} hp."
            )
            embed_data = StatusEffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            combined.embed_data = embed_data_collection

        return combined
