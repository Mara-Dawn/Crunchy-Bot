from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Vulnerable
from combat.status_effects.status_handler import StatusEffectHandler
from config import Config
from control.controller import Controller


class VulnerableHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Vulnerable()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        outcome.modifier = Config.VULNERABLE_SCALING

        embed_data_collection = EmbedDataCollection()
        description = self.status_effect.description
        embed_data = EffectEmbedData(
            self.status_effect, self.status_effect.title, description
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection

        return outcome
