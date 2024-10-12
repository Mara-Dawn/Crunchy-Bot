import datetime

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    OutcomeFlag,
)
from combat.effects.effect_handler import HandlerContext
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import PhysDamageProc
from combat.skills.types import SkillEffect
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class PhysDamageProcHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=PhysDamageProc()
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

        if not handler_context.skill.base_skill.skill_effect.damaging:
            outcome.flags = [OutcomeFlag.NO_CONSUME]
            return outcome

        instances = await self.enchantment_manager.get_enchantment_effect(
            handler_context.source, enchantment, handler_context.context.combat_scale
        )
        instance = instances[0]

        total_damage = await self.actor_manager.get_skill_damage_after_defense(
            handler_context.target, handler_context.skill, instance.scaled_value
        )
        display_damage = await self.actor_manager.get_skill_damage_after_defense(
            handler_context.target, handler_context.skill, instance.value
        )

        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            handler_context.source.id,
            handler_context.target.id,
            enchantment.base_enchantment.enchantment_type,
            total_damage,
            display_damage,
            enchantment.id,
            CombatEventType.ENCHANTMENT_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        embed_data_collection = EmbedDataCollection()
        suffix = " physical"
        if instance.is_crit:
            suffix = " CRITICAL physical"

        description = f"{handler_context.source.name} deals additional {display_damage}{suffix} damage!"
        embed_data = EffectEmbedData(
            enchantment.base_enchantment,
            enchantment.base_enchantment.title,
            description,
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection
        outcome.bonus_damage = instance.value

        return outcome

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return skill_effect == SkillEffect.MAGICAL_DAMAGE
