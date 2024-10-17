from combat.effects.effect import (
    EffectOutcome,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import ExtraGore
from combat.skills.types import SkillEffect
from combat.status_effects.types import StatusEffectType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller


class ExtraGoreHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=ExtraGore()
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

        if handler_context.source.is_enemy:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        if handler_context.status_effect_type != StatusEffectType.BLEED:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        outcome.flags = [OutcomeFlag.ADDITIONAL_STACK_VALUE]
        outcome.value = enchantment.base_enchantment.value

        return outcome

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return False
