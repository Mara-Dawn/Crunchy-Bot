import datetime

from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
    HandlerContext,
)
from combat.enchantments.enchantment import EffectEnchantment
from combat.enchantments.enchantment_handler import EnchantmentEffectHandler
from combat.enchantments.enchantments import DeathSave
from combat.skills.types import SkillEffect
from control.combat.combat_enchantment_manager import CombatEnchantmentManager
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class DeathSaveHandler(EnchantmentEffectHandler):

    def __init__(self, controller: Controller):
        EnchantmentEffectHandler.__init__(
            self, controller=controller, enchantment=DeathSave()
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
        enchantment_type = enchantment.enchantment.base_enchantment.enchantment_type
        if enchantment_type != self.base_enchantment.enchantment_type:
            return outcome

        outcome.value = 1
        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            handler_context.source.id,
            handler_context.source.id,
            enchantment.base_enchantment.enchantment_type,
            1,
            1,
            enchantment.id,
            CombatEventType.ENCHANTMENT_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.target.name} was spared from dying, surviving with 1 health."
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

    async def is_penalty(
        self,
        skill_effect: SkillEffect,
    ) -> bool:
        return False
