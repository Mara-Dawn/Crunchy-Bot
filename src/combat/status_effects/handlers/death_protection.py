import datetime

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import DeathProtection
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class DeathProtectionHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=DeathProtection()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        outcome.value = 1
        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            status_effect.event.source_id,
            status_effect.event.actor_id,
            status_effect.event.status_type,
            1,
            1,
            status_effect.event.id,
            CombatEventType.STATUS_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.target.name} was spared from dying, surviving with 1 health."
        embed_data = EffectEmbedData(
            self.status_effect, self.status_effect.title, description
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection
        outcome.flags = [OutcomeFlag.PREVENT_DEATH]

        return outcome
