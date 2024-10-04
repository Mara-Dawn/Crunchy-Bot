import datetime

from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import (
    ActiveStatusEffect,
    EmbedDataCollection,
    StatusEffectEmbedData,
    StatusEffectOutcome,
)
from combat.status_effects.status_effects import Poison
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from config import Config
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class PoisonHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=Poison()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        outcome = StatusEffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        if handler_context.skill.base_skill.skill_effect in [
            SkillEffect.BUFF,
            SkillEffect.HEALING,
        ]:
            return outcome

        damage_base = handler_context.damage_instance.value
        poison_damage = max(1, int(damage_base * Config.POISON_SCALING))
        damage_display = poison_damage

        actor = handler_context.source
        if actor.is_enemy:
            encounter_scaling = self.actor_manager.get_encounter_scaling(
                actor, handler_context.context.combat_scale
            )
            damage_base = handler_context.damage_instance.value * encounter_scaling
            poison_damage = max(1, int(damage_base * Config.POISON_SCALING))

        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            actor.id,
            actor.id,
            StatusEffectType.POISON,
            poison_damage,
            damage_display,
            None,
            CombatEventType.STATUS_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        outcome.value = damage_display

        embed_data_collection = EmbedDataCollection()
        description = (
            f"{handler_context.source.name} suffers {outcome.value} poison damage."
        )
        embed_data = StatusEffectEmbedData(
            self.status_effect, self.status_effect.title, description
        )
        embed_data_collection.append(embed_data)
        outcome.embed_data = embed_data_collection

        return outcome

    async def combine(
        self, outcomes: list[StatusEffectOutcome], handler_context: HandlerContext
    ) -> StatusEffectOutcome:
        return self.combine_outcomes(outcomes)
