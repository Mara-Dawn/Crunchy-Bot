import random

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Blind
from combat.status_effects.status_handler import StatusEffectHandler
from config import Config
from control.controller import Controller


class BlindHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Blind())

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

        if skill.base_skill.skill_effect in [
            SkillEffect.BUFF,
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
        ]:
            return outcome

        roll = random.random()
        miss_chance = Config.BLIND_MISS_CHANCE

        if handler_context.target.is_enemy and handler_context.target.enemy.is_boss:
            miss_chance = Config.BLIND_BOSS_MISS_CHANCE

        #     blind_count = context.get_applied_status_count(
        #         actor.id, StatusEffectType.BLIND
        #     )
        #     miss_chance *= pow(
        #         Config.BLIND_DIMINISHING_RETURNS, max(0, blind_count - 1)
        #     )

        if roll < miss_chance:
            outcome.modifier = 0
            embed_data_collection = EmbedDataCollection()
            description = f"{handler_context.source.name} misses their attack!"
            embed_data = EffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            outcome.embed_data = embed_data_collection

        return outcome
