from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import CleansingHeal
from combat.skills.types import SkillEffect
from combat.status_effects.types import StatusEffectType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller


class CleansingHealHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=CleansingHeal()
        )
        self.enchantment_manager: CombatEnchantmentManager = (
            self.controller.get_service(CombatEnchantmentManager)
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
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

        if handler_context.skill.base_skill.skill_effect != SkillEffect.HEALING:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        if handler_context.skill.base_skill.aoe:  # noqa: SIM102
            if handler_context.target.id != handler_context.source.id:
                outcome.flags = [OutcomeFlag.NO_CONSUME]

        outcome.modifier = 1 + (enchantment.base_enchantment.value / 100)

        info = []
        for status in handler_context.target.status_effects:
            if status.remaining_stacks <= 0:
                continue
            message = ""
            if StatusEffectType.is_negative(status.status_effect.effect_type):
                await self.status_effect_manager.consume_status_stack(
                    handler_context.context,
                    status,
                    status.remaining_stacks,
                )
                message = f"{status.status_effect.name} was cleansed from {handler_context.target.name}."
                if message != "" and message not in info:
                    info.append(message)
        info = "\n".join(info) if len(info) > 0 else None

        if info is not None:
            embed_data_collection = EmbedDataCollection()
            description = info
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
