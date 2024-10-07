import datetime

from combat.actors import Character, Opponent
from combat.effects.effect import (
    EffectEmbedData,
    EffectOutcome,
    EmbedDataCollection,
)
from combat.effects.effect_handler import HandlerContext
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import Bleed
from combat.status_effects.status_handler import StatusEffectHandler
from config import Config
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class BleedHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(self, controller=controller, status_effect=Bleed())

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()

        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        if handler_context.target.defeated:
            return outcome

        event = status_effect.event

        damage = event.value

        combatant_count = handler_context.context.combat_scale
        encounter_scaling = self.actor_manager.get_encounter_scaling(
            handler_context.target, combatant_count
        )
        damage = event.value
        total_damage = await self.actor_manager.get_damage_after_defense(
            handler_context.target, SkillEffect.EFFECT_DAMAGE, damage
        )

        scaled_damage = max(1, int(total_damage * encounter_scaling))

        event = CombatEvent(
            datetime.datetime.now(),
            handler_context.context.encounter.guild_id,
            handler_context.context.encounter.id,
            event.source_id,
            event.actor_id,
            event.status_type,
            scaled_damage,
            total_damage,
            event.id,
            CombatEventType.STATUS_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(event)

        outcome.value = total_damage

        return outcome

    async def get_application_value(self, handler_context: HandlerContext) -> float:
        if handler_context.source.is_enemy:
            actor: Opponent = handler_context.source
            level = actor.level
            base_value = Config.OPPONENT_DAMAGE_BASE[level] / actor.enemy.damage_scaling
        else:
            actor: Character = handler_context.source
            level = actor.equipment.weapon.level
            base_value = Config.ENEMY_HEALTH_SCALING[level]

        if handler_context.application_value is not None:
            if handler_context.application_value <= 0:
                return 0
            base_value = handler_context.application_value * Config.BLEED_SCALING

        return base_value

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        combined = self.combine_outcomes(outcomes)

        if combined.value is not None:
            embed_data_collection = EmbedDataCollection()
            description = f"{handler_context.target.name} suffers {combined.value} bleeding damage."
            embed_data = EffectEmbedData(
                self.status_effect, self.status_effect.title, description
            )
            embed_data_collection.append(embed_data)
            combined.embed_data = embed_data_collection

        return combined
