from combat.skills.types import SkillType
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    EmbedDataCollection,
    StatusEffectEmbedData,
    StatusEffectOutcome,
)
from combat.status_effects.status_effects import Fear
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from control.controller import Controller


class FearHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Fear())

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        outcome = StatusEffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        skill = handler_context.skill
        if skill is not None and skill.type == SkillType.FEASTING:
            outcome.modifier = 1 + (status_effect.remaining_stacks * 0.2)
            await self.status_effect_manager.consume_status_stack(
                handler_context.context,
                status_effect,
                status_effect.remaining_stacks,
            )

            embed_data_collection = EmbedDataCollection()
            description = "The consumed fear increases the damage taken."
            embed_data = StatusEffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            outcome.embed_data = embed_data_collection

        return outcome

    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        return self.combine_outcomes(outcomes)
