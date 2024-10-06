import datetime

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import RageQuit
from combat.status_effects.status_handler import StatusEffectHandler
from config import Config
from control.controller import Controller
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType


class RageQuitHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=RageQuit()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        actor = handler_context.target

        remaining_health = actor.current_hp / actor.max_hp

        if remaining_health <= Config.RAGE_QUIT_THRESHOLD:
            event = EncounterEvent(
                datetime.datetime.now(),
                handler_context.context.encounter.guild_id,
                handler_context.context.encounter.id,
                self.bot.user.id,
                EncounterEventType.END,
            )
            await self.controller.dispatch_event(event)

            embed_data_collection = EmbedDataCollection()
            description = status_effect.status_effect.description
            embed_data = EffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            outcome.embed_data = embed_data_collection

        return outcome
