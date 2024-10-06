import datetime

from combat.actors import Character, Opponent
from combat.effects.efffect import EffectEmbedData, EffectOutcome, EmbedDataCollection
from combat.gear.types import CharacterAttribute
from combat.skills.types import SkillEffect
from combat.status_effects.status_effect import ActiveStatusEffect
from combat.status_effects.status_effects import PartyLeech
from combat.status_effects.status_handler import HandlerContext, StatusEffectHandler
from combat.status_effects.types import StatusEffectType
from config import Config
from control.controller import Controller
from events.combat_event import CombatEvent
from events.types import CombatEventType


class PartyLeechHandler(StatusEffectHandler):

    def __init__(self, controller: Controller):
        StatusEffectHandler.__init__(
            self, controller=controller, status_effect=PartyLeech()
        )

    async def handle(
        self, status_effect: ActiveStatusEffect, handler_context: HandlerContext
    ) -> EffectOutcome:
        outcome = EffectOutcome.EMPTY()
        effect_type = status_effect.status_effect.effect_type
        if effect_type != self.effect_type:
            return outcome

        context = handler_context.context
        event = status_effect.event
        actor = handler_context.target

        combatant_count = context.combat_scale
        healing = event.value
        total_healing = await self.actor_manager.get_damage_after_defense(
            actor, SkillEffect.HEALING, healing
        )

        scaled_healing = max(1, int(total_healing / 2))

        encounter_scaling = self.actor_manager.get_encounter_scaling(
            actor, combatant_count
        )
        scaled_damage = max(1, int(total_healing * encounter_scaling))

        bleed_event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            event.source_id,
            event.actor_id,
            StatusEffectType.BLEED,
            scaled_damage,
            total_healing,
            event.id,
            CombatEventType.STATUS_EFFECT_OUTCOME,
        )
        await self.controller.dispatch_event(bleed_event)

        for combatant in context.active_combatants:

            heal_event = CombatEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                event.source_id,
                combatant.id,
                event.status_type,
                scaled_healing,
                scaled_healing,
                event.id,
                CombatEventType.STATUS_EFFECT_OUTCOME,
            )
            await self.controller.dispatch_event(heal_event)

        outcome.value = (total_healing, scaled_healing)

        return outcome

    async def get_application_value(self, handler_context: HandlerContext) -> float:
        if handler_context.source.is_enemy:
            opponent: Opponent = handler_context.source
            level = opponent.level
            base_value = (
                Config.OPPONENT_DAMAGE_BASE[level] / opponent.enemy.damage_scaling
            )
            healing_modifier = opponent.enemy.attributes[
                CharacterAttribute.HEALING_BONUS
            ]
        else:
            actor: Character = handler_context.source
            level = actor.equipment.weapon.level
            base_value = Config.ENEMY_HEALTH_SCALING[level]
            healing_modifier = actor.equipment.attributes[
                CharacterAttribute.HEALING_BONUS
            ]

        if handler_context.application_value is not None:
            if handler_context.application_value <= 0:
                return 0
            base_value = handler_context.application_value * Config.LEECH_SCALING

        return base_value * (1 + healing_modifier)

    async def combine(
        self, outcomes: list[EffectOutcome], handler_context: HandlerContext
    ) -> EffectOutcome:
        combined = EffectOutcome.EMPTY()
        combined.value = (0, 0)

        for outcome in outcomes:
            combined_damage = outcome.value[0] + combined.value[0]
            combined_healing = outcome.value[1] + combined.value[1]
            combined.value = (combined_damage, combined_healing)

        embed_data_collection = EmbedDataCollection()
        description = f"{handler_context.target.name} suffers {combined.value[0]} damage.\nEveryone heals for {combined.value[1]} hp."
        embed_data = EffectEmbedData(
            self.status_effect, self.status_effect.title, description
        )
        embed_data_collection.append(embed_data)
        combined.embed_data = embed_data_collection

        return combined
