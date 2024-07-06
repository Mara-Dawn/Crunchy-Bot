import datetime
import random
from sys import activate_stack_trampoline
from typing import Any

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.gear.types import CharacterAttribute
from combat.skills.skill import Skill
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
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.object_factory import ObjectFactory
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
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.NEW_ROUND:
                        await self.trigger_effects(StatusEffectTrigger.START_OF_ROUND)

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
                    if application_value <= 0:
                        return
                    base_value = max(
                        base_value, (application_value * Config.BLEED_SCALING)
                    )

                damage = base_value * (1 + modifier)

        status_effect = await self.factory.get_status_effect(type)
        if status_effect.override or status_effect.override_by_actor:
            for active_effect in target.status_effects:
                override = False
                if active_effect.status_effect.effect_type != type:
                    continue
                if status_effect.override and active_effect.remaining_stacks > 0:
                    override = True
                if (
                    status_effect.override_by_actor
                    and active_effect.event.get_causing_user_id == source.id
                ):
                    override = True
                if override:
                    await self.consume_status_stack(
                        context,
                        active_effect,
                        active_effect.remaining_stacks,
                    )

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
                    encounter_scaling = self.actor_manager.get_encounter_scaling(
                        actor, combatant_count
                    )
                    damage = event.value
                    scaled_damage = damage * encounter_scaling
                    total_damage = await self.actor_manager.get_damage_after_defense(
                        actor, SkillEffect.STATUS_EFFECT_DAMAGE, damage
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
                case StatusEffectType.BLIND:
                    roll = random.random()
                    effect_data[effect_type] = (
                        0 if roll < Config.BLIND_MISS_CHANCE else 1
                    )

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
            status_effect = await self.factory.get_status_effect(effect_type)

            match effect_type:
                case StatusEffectType.CLEANSE:
                    title = f"{status_effect.emoji} Cleanse"
                    description = data
                case StatusEffectType.BLEED:
                    title = f"{status_effect.emoji} Bleed"
                    description = f"{actor.name} suffers {data} bleeding damage."
                case StatusEffectType.BLIND:
                    if data != 0:
                        continue
                    title = f"{status_effect.emoji} Blind"
                    description = f"{actor.name} misses their attack!."

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

    async def handle_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
        status_effects: list[ActiveStatusEffect],
    ) -> tuple[dict[str, str], float]:
        if not skill.base_skill.modifiable:
            return None, 1

        effect_data = await self.get_status_effect_outcomes(
            context, actor, status_effects
        )

        modifier = 1
        for _, data in effect_data.items():
            modifier *= float(data)

        embed_data = await self.get_status_effect_outcome_info(
            context, actor, effect_data
        )

        return embed_data, modifier

    async def actor_trigger(
        self, context: EncounterContext, actor: Actor, trigger: StatusEffectTrigger
    ) -> list[ActiveStatusEffect]:
        triggered = []

        for active_status_effect in actor.status_effects:
            if active_status_effect.remaining_stacks <= 0:
                continue

            status_effect = active_status_effect.status_effect

            if trigger in status_effect.consumed:
                await self.consume_status_stack(context, active_status_effect)

            if trigger in status_effect.trigger:
                triggered.append(active_status_effect)

        triggered = sorted(
            triggered, key=lambda item: item.status_effect.priority, reverse=True
        )
        return triggered

    async def trigger_effects(self, trigger: StatusEffectTrigger):
        pass
