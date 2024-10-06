from combat.effects.efffect import EffectEmbedData, EffectOutcome, EmbedDataCollection
from combat.skills.types import SkillType
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Chuckle
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller


class ChuckleHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Chuckle()
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        skill = handler_context.skill
        if skill is not None and skill.type == SkillType.HIDDEN_BADASS:
            outcome.modifier = status_effect.remaining_stacks * 3
            await self.status_effect_manager.consume_status_stack(
                handler_context.context,
                status_effect,
                status_effect.remaining_stacks,
            )

            embed_data_collection = EmbedDataCollection()
            description = "They burst out in laughter and take increased damage."
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
