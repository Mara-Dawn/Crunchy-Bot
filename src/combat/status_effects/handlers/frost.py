from combat.effects.efffect import EffectEmbedData, EffectOutcome, EmbedDataCollection
from combat.effects.types import EffectTrigger
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Frost
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from config import Config
from control.controller import Controller


class FrostHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Frost())

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        match handler_context.trigger:
            case EffectTrigger.ATTRIBUTE:
                outcome.initiative = -Config.FROST_DEX_PENALTY
            case EffectTrigger.ON_ATTACK:
                if handler_context.skill.base_skill.skill_effect in [
                    SkillEffect.HEALING,
                ]:
                    outcome.modifier = Config.FROST_HEAL_MODIFIER
                    embed_data_collection = EmbedDataCollection()
                    description = "Healing effectiveness was reduced by frost."
                    embed_data = EffectEmbedData(
                        self.status_effect, self.status_effec.title, description
                    )
                    embed_data_collection.append(embed_data)
                    outcome.embed_data = embed_data_collection

        return outcome

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        return self.combine_outcomes(outcomes)
