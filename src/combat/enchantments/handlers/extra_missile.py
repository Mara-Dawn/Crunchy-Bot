from combat.effects.effect import (
    EffectOutcome,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.effects.types import EffectTrigger
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import ExtraMissile
from combat.skills.types import SkillEffect, SkillType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller


class ExtraMissileHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=ExtraMissile()
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
            return outcome

        if handler_context.skill.base_skill.skill_type not in [
            SkillType.PHYSICAL_MISSILE,
            SkillType.MAGIC_MISSILE,
        ]:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        match handler_context.trigger:
            case EffectTrigger.SKILL_HITS:
                outcome.flags = [OutcomeFlag.NO_CONSUME]
                outcome.value = enchantment.base_enchantment.value
            case EffectTrigger.ON_ATTACK:
                pass
        return outcome

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return False
