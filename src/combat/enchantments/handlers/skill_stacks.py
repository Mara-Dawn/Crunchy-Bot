from combat.effects.effect import (
    EffectOutcome,
)
from combat.effects.effect_handler import HandlerContext
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import SkillStacks, SkillStacksProxy
from combat.skills.types import SkillEffect
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller


class SkillStacksHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=SkillStacksProxy()
        )
        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
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

        base_enchantment: SkillStacks = enchantment.base_enchantment

        if handler_context.skill.base_skill.skill_type != base_enchantment.skill_type:
            return outcome

        outcome.value = base_enchantment.value
        return outcome

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return False
