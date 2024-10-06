from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Simp
from combat.status_effects.status_handler import StatusEffectHandler
from control.controller import Controller


class SimpHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Simp())

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
        outcome.modifier = 0.5

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.target.name}'s attacks are half as effective!"
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
