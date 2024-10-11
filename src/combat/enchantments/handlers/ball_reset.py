import random

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import BallReset
from combat.skills.types import SkillEffect, SkillType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller


class BallResetHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=BallReset()
        )
        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )

    async def handle(
        self,
        enchantment: EffectEnchantment,
        handler_context: HandlerContext,
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        enchantment_type = enchantment.base_enchantment.enchantment_type
        if enchantment_type != self.base_enchantment.enchantment_type:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome
        skill_type = handler_context.skill.base_skill.skill_type

        if skill_type not in [
            SkillType.FIRE_BALL,
            SkillType.ICE_BALL,
        ]:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        if random.random() > (enchantment.base_enchantment.value / 100):
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        handler_context.source.skill_cooldowns[skill_type] = None

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.skill.name} cooldown was reset!"
        embed_data = EffectEmbedData(
            enchantment.base_enchantment,
            enchantment.base_enchantment.title,
            description,
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection

        return outcome

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return False
