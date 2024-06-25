import datetime
from typing import Any

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.gear.types import CharacterAttribute
from combat.skills.status_effect import (
    ActiveStatusEffect,
    SkillStatusEffect,
    StatusEffect,
)
from combat.skills.status_effects import *  # noqa: F403
from combat.skills.types import (
    SkillEffect,
    StatusEffectTrigger,
    StatusEffectType,
)
from config import Config
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType, EncounterEventType, EventType


class CombatStatusEffectManager(Service):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.log_name = "Combat Skills"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.NEW_ROUND:
                        await self.trigger_effects(StatusEffectTrigger.START_OF_ROUND)

    async def get_status_effect(self, status_type: StatusEffectType) -> StatusEffect:
        status_effect = globals()[status_type]
        return status_effect()

    async def apply_skill_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        skill_status_effect: SkillStatusEffect,
    ):
        pass

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        stacks: int,
        application_value: float = None,
    ):
        damage = 0
        match type:
            case StatusEffectType.BLEED:
                if source.is_enemy:
                    actor: Opponent = source
                    level = actor.level
                    base_value = (
                        Config.OPPONENT_DAMAGE_BASE[level] / actor.enemy.damage_scaling
                    )
                    modifier = actor.enemy.attributes[
                        CharacterAttribute.PHYS_DAMAGE_INCREASE
                    ]
                else:
                    actor: Character = source
                    level = actor.equipment.weapon.level
                    base_value = Config.ENEMY_HEALTH_SCALING[level]
                    modifier = actor.equipment.attributes[
                        CharacterAttribute.PHYS_DAMAGE_INCREASE
                    ]

                if application_value is not None:
                    base_value = max(
                        base_value, (application_value * Config.BLEED_SCALING)
                    )

                damage = base_value * (1 + modifier)

        event = StatusEffectEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            source.id,
            target.id,
            type,
            stacks,
            damage,
        )
        await self.controller.dispatch_event(event)

    async def consume_status_stack(
        self,
        context: EncounterContext,
        status_effect: ActiveStatusEffect,
        amount: int = 1,
    ):
        status_effect_event = status_effect.event
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            status_effect_event.actor_id,
            status_effect_event.actor_id,
            status_effect_event.status_type,
            -amount,
            status_effect_event.id,
            CombatEventType.STATUS_EFFECT,
        )
        await self.controller.dispatch_event(event)

    async def get_status_effect_outcomes(
        self,
        context: EncounterContext,
        actor: Actor,
        status_effects: list[ActiveStatusEffect],
    ) -> dict[StatusEffectType, Any]:
        effect_data: dict[StatusEffectType, Any] = {}

        for active_status_effect in status_effects:
            event = active_status_effect.event
            effect_type = active_status_effect.status_effect.effect_type

            match effect_type:
                case StatusEffectType.CLEANSE:
                    for status in status_effects:
                        if status.status_effect.effect_type == StatusEffectType.BLEED:
                            await self.consume_status_stack(
                                context,
                                status,
                                status.remaining_stacks,
                            )
                            effect_data[effect_type] = "Bleed was cleansed."

                case StatusEffectType.BLEED:
                    if StatusEffectType.CLEANSE in [
                        x.status_effect.effect_type for x in status_effects
                    ]:
                        continue
                    damage = event.value

                    combatant_count = context.get_combat_scale()
                    encounter_scaling = actor.get_encounter_scaling(combatant_count)
                    damage = event.value
                    scaled_damage = damage * encounter_scaling
                    total_damage = actor.get_damage_after_defense(
                        SkillEffect.STATUS_EFFECT_DAMAGE, damage
                    )

                    scaled_damage = total_damage * encounter_scaling

                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        event.source_id,
                        event.actor_id,
                        event.status_type,
                        scaled_damage,
                        event.id,
                        CombatEventType.STATUS_EFFECT_OUTCOME,
                    )
                    await self.controller.dispatch_event(event)

                    if effect_type not in effect_data:
                        effect_data[effect_type] = total_damage
                    else:
                        effect_data[effect_type] += total_damage

        return effect_data

    async def get_status_effect_outcome_info(
        self,
        context: EncounterContext,
        actor: Actor,
        effect_data: dict[StatusEffectType, Any],
    ) -> dict[str, str]:
        outcome_info = {}
        for effect_type, data in effect_data.items():
            title = ""
            description = ""
            status_effect = await self.get_status_effect(effect_type)

            match effect_type:
                case StatusEffectType.CLEANSE:
                    title = f"{status_effect.emoji} Cleanse"
                    description = data
                case StatusEffectType.BLEED:
                    title = f"{status_effect.emoji} Bleed"
                    description = f"{actor.name} suffers {data} bleeding damage."

            outcome_info[title] = description

        return outcome_info

    async def handle_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        status_effects: list[ActiveStatusEffect],
    ) -> dict[str, str]:
        effect_data = await self.get_status_effect_outcomes(
            context, actor, status_effects
        )
        return await self.get_status_effect_outcome_info(context, actor, effect_data)

    async def actor_trigger(
        self, context: EncounterContext, actor: Actor, trigger: StatusEffectTrigger
    ) -> list[ActiveStatusEffect]:
        triggered = []

        for active_status_effect in actor.status_effects:
            status_effect = active_status_effect.status_effect

            if trigger in status_effect.trigger:
                triggered.append(active_status_effect)
                await self.consume_status_stack(context, active_status_effect)

        triggered = sorted(
            triggered, key=lambda item: item.status_effect.priority, reverse=True
        )
        return triggered

    async def trigger_effects(self, trigger: StatusEffectTrigger):
        pass
