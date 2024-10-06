import random

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Evasive
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller


class EvasiveHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Evasive()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()

        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        skill = handler_context.skill
        if skill is not None and not skill.base_skill.modifiable:
            return outcome

        chance_to_evade = status_effect.event.value / 100
        roll = random.random()

        if roll < chance_to_evade:
            outcome.modifier = 0

            embed_data_collection = EmbedDataCollection()
            description = outcome.info
            title = f"{self.status_effect.emoji} Miss"
            description = f"{handler_context.target.name} dodged an attack!"
            embed_data = EffectEmbedData(self.status_effect, title, description)
            embed_data_collection.append(embed_data)
            outcome.embed_data = embed_data_collection

        return outcome
