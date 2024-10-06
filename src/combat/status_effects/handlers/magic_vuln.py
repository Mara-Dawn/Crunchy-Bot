from combat.effects.efffect import EffectEmbedData, EffectOutcome, EmbedDataCollection
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import MagicVuln
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from config import Config
from control.controller import Controller


class MagicVulnHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=MagicVuln()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        if handler_context.skill.base_skill.skill_effect != SkillEffect.MAGICAL_DAMAGE:
            return outcome

        outcome.modifier = Config.MAGIC_VULN_SCALING

        embed_data_collection = EmbedDataCollection()
        description = self.status_effect.description
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
