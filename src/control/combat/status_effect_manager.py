import datetime
import random

from discord.ext import commands

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.gear.types import CharacterAttribute
from combat.skills.skill import Skill, SkillInstance
from combat.skills.status_effect import (
    ActiveStatusEffect,
    EmbedDataCollection,
    StatusEffectEmbedData,
    StatusEffectOutcome,
)
from combat.skills.status_effects import *  # noqa: F403
from combat.skills.types import (
    SkillEffect,
    SkillType,
    StatusEffectTrigger,
    StatusEffectType,
)
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import CombatEventType, EncounterEventType


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
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)

    async def listen_for_event(self, event: BotEvent):
        pass

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        stacks: int,
        application_value: float = None,
    ) -> StatusEffectType | None:
        if type == StatusEffectType.RANDOM:
            random_positive_effect = [
                StatusEffectType.HIGH,
                StatusEffectType.RAGE,
            ]
            random_negative_effect = [
                StatusEffectType.BLEED,
                StatusEffectType.BLIND,
                StatusEffectType.POISON,
            ]

            chance_for_positive = Config.RANDOM_POSITIVE_CHANCE
            if random.random() < chance_for_positive:
                type = random.choice(random_positive_effect)
            else:
                type = random.choice(random_negative_effect)

        status_effect = await self.factory.get_status_effect(type)

        if (
            application_value is not None
            and application_value == 0
            and not status_effect.apply_on_miss
        ):
            return None

        for active_actor in context.current_initiative:
            if active_actor.id == source.id:
                source = active_actor
            if active_actor.id == target.id:
                target = active_actor

        damage = 0
        match type:
            case StatusEffectType.BLEED:
                if source.is_enemy:
                    actor: Opponent = source
                    level = actor.level
                    base_value = (
                        Config.OPPONENT_DAMAGE_BASE[level] / actor.enemy.damage_scaling
                    )
                else:
                    actor: Character = source
                    level = actor.equipment.weapon.level
                    base_value = Config.ENEMY_HEALTH_SCALING[level]

                if application_value is not None:
                    if application_value <= 0:
                        return None
                    base_value = application_value * Config.BLEED_SCALING

                damage = base_value
            case StatusEffectType.PARTY_LEECH:
                if source.is_enemy:
                    opponent: Opponent = source
                    level = opponent.level
                    base_value = (
                        Config.OPPONENT_DAMAGE_BASE[level]
                        / opponent.enemy.damage_scaling
                    )
                    healing_modifier = opponent.enemy.attributes[
                        CharacterAttribute.HEALING_BONUS
                    ]
                else:
                    actor: Character = source
                    level = actor.equipment.weapon.level
                    base_value = Config.ENEMY_HEALTH_SCALING[level]
                    healing_modifier = actor.equipment.attributes[
                        CharacterAttribute.HEALING_BONUS
                    ]

                if application_value is not None:
                    if application_value <= 0:
                        return None
                    base_value = application_value * Config.LEECH_SCALING

                damage = base_value * (1 + healing_modifier)
            case (
                StatusEffectType.INSPIRED
                | StatusEffectType.HEAL_OVER_TIME
                | StatusEffectType.EVASIVE
                | StatusEffectType.PROTECTION
                | StatusEffectType.NEURON_ACTIVE
            ):
                damage = application_value

        if (
            status_effect.override
            or status_effect.override_by_actor
            or status_effect.stack
        ):
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
                if status_effect.stack and active_effect.remaining_stacks > 0:
                    override = True
                    stacks += active_effect.remaining_stacks
                if override:
                    await self.consume_status_stack(
                        context,
                        active_effect,
                        active_effect.remaining_stacks,
                    )

        stacks = min(stacks, status_effect.max_stacks)

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

        return type

    async def handle_on_application_status_effects(
        self,
        actor: Actor,
        context: EncounterContext,
        effect_type: StatusEffectType,
    ) -> StatusEffectOutcome:
        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_APPLICATION
        )

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        filtered = []
        for effect in triggered_status_effects:
            if effect.status_effect.effect_type == effect_type:
                filtered.append(effect)

        outcomes = await self.get_status_effect_outcomes(
            StatusEffectTrigger.ON_APPLICATION,
            context,
            actor,
            filtered,
        )

        embed_data = await self.get_status_effect_outcome_info(
            StatusEffectTrigger.ON_DAMAGE_TAKEN, context, actor, outcomes
        )

        combined = self.combine_outcomes(outcomes.values(), embed_data)

        return combined

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
            -amount,
            status_effect_event.id,
            CombatEventType.STATUS_EFFECT,
        )
        await self.controller.dispatch_event(event)

    async def handle_attribute_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> StatusEffectOutcome:

        triggered_status_effects = []
        for active_status_effect in actor.status_effects:
            if active_status_effect.remaining_stacks <= 0:
                continue

            status_effect = active_status_effect.status_effect

            if (
                status_effect.delay_consume
                and active_status_effect.event.id > context.round_event_id_cutoff
            ):
                continue

            if StatusEffectTrigger.ATTRIBUTE in status_effect.trigger:
                triggered_status_effects.append(active_status_effect)

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            StatusEffectTrigger.ATTRIBUTE, None, actor, triggered_status_effects
        )

        combined = self.combine_outcomes(outcomes.values(), None)

        return combined

    async def get_status_effect_outcomes(
        self,
        trigger: StatusEffectTrigger,
        context: EncounterContext,
        actor: Actor,
        status_effects: list[ActiveStatusEffect],
        skill: Skill = None,
    ) -> dict[StatusEffectType, StatusEffectOutcome]:
        effect_data: dict[StatusEffectType, StatusEffectOutcome] = {}

        for active_status_effect in status_effects:
            event = active_status_effect.event
            effect_type = active_status_effect.status_effect.effect_type

            value = None
            modifier = None
            crit_chance = None
            crit_chance_modifier = None
            initiative = None
            info = None

            match effect_type:
                case StatusEffectType.CLEANSE:
                    info = []
                    for status in actor.status_effects:
                        message = ""
                        if status.status_effect.effect_type == StatusEffectType.BLEED:
                            await self.consume_status_stack(
                                context,
                                status,
                                status.remaining_stacks,
                            )
                            message = f"Bleed was cleansed from {actor.name}."
                        if status.status_effect.effect_type == StatusEffectType.POISON:
                            await self.consume_status_stack(
                                context,
                                status,
                                status.remaining_stacks,
                            )
                            message = f"Poison was cleansed from {actor.name}."
                        if message != "" and message not in info:
                            info.append(message)
                    info = "\n".join(info) if len(info) > 0 else None
                case StatusEffectType.BLEED:
                    if StatusEffectType.CLEANSE in [
                        x.status_effect.effect_type for x in status_effects
                    ]:
                        continue
                    damage = event.value

                    combatant_count = context.combat_scale
                    encounter_scaling = self.actor_manager.get_encounter_scaling(
                        actor, combatant_count
                    )
                    damage = event.value
                    total_damage = await self.actor_manager.get_damage_after_defense(
                        actor, SkillEffect.STATUS_EFFECT_DAMAGE, damage
                    )

                    scaled_damage = max(1, int(total_damage * encounter_scaling))

                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        event.source_id,
                        event.actor_id,
                        event.status_type,
                        scaled_damage,
                        total_damage,
                        event.id,
                        CombatEventType.STATUS_EFFECT_OUTCOME,
                    )
                    await self.controller.dispatch_event(event)

                    if effect_type not in effect_data:
                        value = total_damage
                    else:
                        value = effect_data[effect_type].value + total_damage
                case StatusEffectType.PARTY_LEECH:
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

                    if effect_type not in effect_data:
                        value = (total_healing, scaled_healing)
                    else:
                        combined_damage = (
                            effect_data[effect_type].value[0] + total_healing
                        )
                        combined_healing = (
                            effect_data[effect_type].value[1] + scaled_healing
                        )
                        value = (combined_damage, combined_healing)
                case StatusEffectType.HEAL_OVER_TIME:
                    healing = int(event.value)
                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        event.source_id,
                        event.actor_id,
                        event.status_type,
                        healing,
                        healing,
                        event.id,
                        CombatEventType.STATUS_EFFECT_OUTCOME,
                    )
                    await self.controller.dispatch_event(event)

                    if effect_type not in effect_data:
                        value = healing
                    else:
                        value = effect_data[effect_type].value + healing
                case StatusEffectType.BLIND:
                    if skill is not None and not skill.base_skill.modifiable:
                        continue
                    if skill.base_skill.skill_effect in [
                        SkillEffect.BUFF,
                        SkillEffect.NOTHING,
                        SkillEffect.HEALING,
                    ]:
                        continue
                    roll = random.random()
                    miss_chance = Config.BLIND_MISS_CHANCE

                    if actor.is_enemy and actor.enemy.is_boss:
                        miss_chance = Config.BLIND_BOSS_MISS_CHANCE
                    #     blind_count = context.get_applied_status_count(
                    #         actor.id, StatusEffectType.BLIND
                    #     )
                    #     miss_chance *= pow(
                    #         Config.BLIND_DIMINISHING_RETURNS, max(0, blind_count - 1)
                    #     )

                    modifier = 0 if roll < miss_chance else 1
                case StatusEffectType.EVASIVE:
                    if skill is not None and not skill.base_skill.modifiable:
                        continue
                    chance_to_evade = active_status_effect.event.value / 100
                    roll = random.random()
                    modifier = 0 if roll < chance_to_evade else 1
                case StatusEffectType.FLUSTERED:
                    if skill.base_skill.skill_effect in [
                        SkillEffect.BUFF,
                        SkillEffect.NOTHING,
                        SkillEffect.HEALING,
                    ]:
                        continue
                    modifier = 0
                case StatusEffectType.SIMP:
                    if skill.base_skill.skill_effect in [
                        SkillEffect.BUFF,
                        SkillEffect.NOTHING,
                        SkillEffect.HEALING,
                    ]:
                        continue
                    modifier = 0.5
                case StatusEffectType.FROST:
                    match trigger:
                        case StatusEffectTrigger.ATTRIBUTE:
                            if effect_type not in effect_data:
                                initiative = -Config.FROST_DEX_PENALTY
                            else:
                                initiative = (
                                    effect_data[effect_type].initiative
                                    - Config.FROST_DEX_PENALTY
                                )
                        case StatusEffectTrigger.ON_ATTACK:
                            if skill.base_skill.skill_effect in [
                                SkillEffect.HEALING,
                            ]:
                                modifier = Config.FROST_HEAL_MODIFIER
                                info = "Healing effectiveness was reduced by frost."
                case StatusEffectType.STUN:
                    modifier = 1
                    event = EncounterEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        actor.id,
                        EncounterEventType.FORCE_SKIP,
                    )
                    await self.controller.dispatch_event(event)
                case StatusEffectType.FROGGED:
                    roll = random.random()
                    modifier = 0 if roll < Config.FROGGED_FAIL_CHANCE else 1
                    if modifier == 0:
                        event = EncounterEvent(
                            datetime.datetime.now(),
                            context.encounter.guild_id,
                            context.encounter.id,
                            actor.id,
                            EncounterEventType.FORCE_SKIP,
                        )
                        await self.controller.dispatch_event(event)
                case StatusEffectType.INSPIRED | StatusEffectType.NEURON_ACTIVE:
                    if skill.base_skill.skill_effect in [
                        SkillEffect.BUFF,
                        SkillEffect.NOTHING,
                        SkillEffect.HEALING,
                    ]:
                        continue
                    modifier = 1 + (active_status_effect.event.value / 100)
                case StatusEffectType.ZONED_IN:
                    crit_chance = 1
                case StatusEffectType.PROTECTION:
                    modifier = 1 - (active_status_effect.event.value / 100)
                    info = "Attack damage was reduced."
                case StatusEffectType.FEAR:
                    if skill is not None and skill.type == SkillType.FEASTING:
                        modifier = 1 + (active_status_effect.remaining_stacks * 0.2)
                        await self.consume_status_stack(
                            context,
                            active_status_effect,
                            active_status_effect.remaining_stacks,
                        )
                case StatusEffectType.HIGH:
                    modifier = 0.5 + random.random() * 1.5
                case StatusEffectType.DEATH_PROTECTION:
                    value = 1
                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        event.source_id,
                        event.actor_id,
                        event.status_type,
                        1,
                        1,
                        event.id,
                        CombatEventType.STATUS_EFFECT_OUTCOME,
                    )
                    await self.controller.dispatch_event(event)
                case StatusEffectType.RAGE_QUIT:
                    current_hp = actor.current_hp
                    remaining_health = current_hp / actor.max_hp
                    if remaining_health <= Config.RAGE_QUIT_THRESHOLD:
                        event = EncounterEvent(
                            datetime.datetime.now(),
                            context.encounter.guild_id,
                            context.encounter.id,
                            self.bot.user.id,
                            EncounterEventType.END,
                        )
                        await self.controller.dispatch_event(event)
                        info = active_status_effect.status_effect.description

            effect_data[effect_type] = StatusEffectOutcome(
                value,
                modifier,
                crit_chance,
                crit_chance_modifier,
                initiative,
                info,
                None,
            )
        return effect_data

    async def get_status_effect_outcome_info(
        self,
        trigger: StatusEffectTrigger,
        context: EncounterContext,
        actor: Actor,
        effect_data: dict[StatusEffectType, StatusEffectOutcome],
    ) -> EmbedDataCollection:
        embed_data_collection = EmbedDataCollection()
        for effect_type, outcome in effect_data.items():
            status_effect = await self.factory.get_status_effect(effect_type)
            title = f"{status_effect.emoji} {status_effect.name}"
            description = ""

            match effect_type:
                case StatusEffectType.CLEANSE:
                    if outcome.info is not None:
                        description = outcome.info
                case StatusEffectType.BLEED:
                    description = (
                        f"{actor.name} suffers {outcome.value} bleeding damage."
                    )
                case StatusEffectType.HEAL_OVER_TIME:
                    description = f"{actor.name} heals for {outcome.value} hp."
                case StatusEffectType.PARTY_LEECH:
                    description = f"{actor.name} suffers {outcome.value[0]} damage.\nEveryone heals for {outcome.value[1]} hp."
                case StatusEffectType.POISON:
                    description = f"{actor.name} suffers {outcome.value} poison damage."
                case StatusEffectType.BLIND:
                    if outcome.modifier != 0:
                        continue
                    description = f"{actor.name} misses their attack!"
                case StatusEffectType.PROTECTION:
                    description = outcome.info
                case StatusEffectType.FROST:
                    match trigger:
                        case StatusEffectTrigger.ON_ATTACK:
                            if outcome.info is not None:
                                description = outcome.info
                case StatusEffectType.EVASIVE:
                    if outcome.modifier != 0:
                        continue
                    title = f"{status_effect.emoji} Miss"
                    description = f"{actor.name} dodged an attack!"
                case StatusEffectType.FLUSTERED:
                    description = f"{actor.name} cannot harm their opponent!"
                case StatusEffectType.SIMP:
                    description = f"{actor.name}'s attacks are half as effective!"
                case StatusEffectType.FEAR:
                    if outcome.modifier is not None:
                        description = "The consumed fear increases the damage taken."
                case StatusEffectType.HIGH:
                    description = f"{actor.name} is blazed out of their mind causing unexpected skill outcomes."
                case StatusEffectType.RAGE_QUIT:
                    if outcome.info is not None:
                        description = outcome.info
                case StatusEffectType.FROGGED:
                    if outcome.modifier != 0:
                        continue
                    description = "You are a frog and fail your action."
                case StatusEffectType.STUN:
                    description = "You are stunned."
                case StatusEffectType.DEATH_PROTECTION:
                    if outcome.value == 1:
                        description = f"{actor.name} was spared from dying, surviving with 1 health."

            if description != "":
                embed_data = StatusEffectEmbedData(status_effect, title, description)
                embed_data_collection.append(embed_data)

        if embed_data_collection.length <= 0:
            return None
        return embed_data_collection

    def combine_outcomes(
        self,
        outcomes: list[StatusEffectOutcome],
        embed_data_collection: EmbedDataCollection | None,
    ) -> StatusEffectOutcome:
        value = None
        modifier = None
        crit_chance = None
        crit_chance_modifier = None
        info = None
        initiative = None

        for outcome in outcomes:
            if outcome.value is not None and isinstance(outcome.value, int | float):
                if value is None:
                    value = outcome.value
                else:
                    value += outcome.value

            if outcome.modifier is not None:
                if modifier is None:
                    modifier = outcome.modifier
                else:
                    modifier *= outcome.modifier

            if outcome.crit_chance is not None:  # noqa: SIM102
                if crit_chance is None or crit_chance < outcome.crit_chance:
                    crit_chance = outcome.crit_chance

            if outcome.crit_chance_modifier is not None:
                if crit_chance_modifier is None:
                    crit_chance_modifier = outcome.crit_chance_modifier
                else:
                    crit_chance_modifier *= outcome.crit_chance_modifier

            if outcome.initiative is not None:
                if initiative is None:
                    initiative = outcome.initiative
                else:
                    initiative += outcome.initiative

            if outcome.info is not None:
                if info is None:
                    info = outcome.info
                else:
                    info += "\n" + outcome.info

        return StatusEffectOutcome(
            value,
            modifier,
            crit_chance,
            crit_chance_modifier,
            initiative,
            info,
            embed_data_collection,
        )

    async def handle_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> StatusEffectOutcome:
        skill_effect = skill.base_skill.skill_effect

        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_ATTACK
        )

        if len(triggered_status_effects) <= 0 or skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.BUFF,
        ]:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            StatusEffectTrigger.ON_ATTACK,
            context,
            actor,
            triggered_status_effects,
            skill=skill,
        )

        embed_data = await self.get_status_effect_outcome_info(
            StatusEffectTrigger.ON_ATTACK, context, actor, outcomes
        )

        combined = self.combine_outcomes(outcomes.values(), embed_data)

        if not skill.base_skill.modifiable:
            if combined.modifier is not None:
                combined.modifier = max(1, combined.modifier)
            combined.crit_chance = None
            combined.crit_chance_modifier = None

        return combined

    async def handle_on_damage_taken_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> StatusEffectOutcome:
        skill_effect = skill.base_skill.skill_effect

        if skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
            SkillEffect.BUFF,
        ]:
            return StatusEffectOutcome.EMPTY()

        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_DAMAGE_TAKEN
        )

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            StatusEffectTrigger.ON_DAMAGE_TAKEN,
            context,
            actor,
            triggered_status_effects,
            skill=skill,
        )

        embed_data = await self.get_status_effect_outcome_info(
            StatusEffectTrigger.ON_DAMAGE_TAKEN, context, actor, outcomes
        )

        combined = self.combine_outcomes(outcomes.values(), embed_data)

        if not skill.base_skill.modifiable:
            if combined.modifier is not None:
                combined.modifier = max(1, combined.modifier)
            combined.crit_chance = None
            combined.crit_chance_modifier = None

        return combined

    async def handle_on_death_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> StatusEffectOutcome:
        for active_actor in context.current_initiative:
            if active_actor.id == actor.id:
                actor = active_actor

        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_DEATH
        )

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            StatusEffectTrigger.ON_DEATH, context, actor, triggered_status_effects
        )

        embed_data = await self.get_status_effect_outcome_info(
            StatusEffectTrigger.ON_DEATH, context, actor, outcomes
        )
        return self.combine_outcomes(outcomes.values(), embed_data)

    async def handle_post_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        target: Actor,
        skill: Skill,
        damage_instance: SkillInstance,
    ) -> tuple[StatusEffectOutcome, list[tuple[StatusEffectType, int]]]:
        current_actor = context.get_actor_by_id(actor.id)
        current_target = context.get_actor_by_id(target.id)
        outcomes: dict[StatusEffectType, StatusEffectOutcome] = {}
        triggered_status_effects = await self.actor_trigger(
            context, current_actor, StatusEffectTrigger.POST_ATTACK
        )

        applied_status_effects: list[tuple[StatusEffectType, int]] = []

        for triggered_status_effect in triggered_status_effects:
            effect_type = triggered_status_effect.status_effect.effect_type

            value = None
            modifier = None
            crit_chance = None
            crit_chance_modifier = None
            initiative = None
            info = None

            match effect_type:
                case StatusEffectType.RAGE:
                    damage = damage_instance.value
                    if actor.is_enemy:
                        damage = damage_instance.scaled_value

                    applied_status_type = await self.apply_status(
                        context,
                        current_actor,
                        current_target,
                        StatusEffectType.BLEED,
                        3,
                        damage,
                    )
                    if applied_status_type is not None:
                        applied_status_effects.append(
                            (
                                StatusEffectType.BLEED,
                                3,
                            )
                        )
                case StatusEffectType.POISON:
                    if StatusEffectType.CLEANSE in [
                        x.status_effect.effect_type for x in triggered_status_effects
                    ]:
                        continue
                    if skill.base_skill.skill_effect in [
                        SkillEffect.BUFF,
                        SkillEffect.HEALING,
                    ]:
                        continue

                    damage_base = damage_instance.value
                    poison_damage = max(1, int(damage_base * Config.POISON_SCALING))
                    damage_display = poison_damage

                    if actor.is_enemy:
                        encounter_scaling = self.actor_manager.get_encounter_scaling(
                            actor, context.combat_scale
                        )
                        damage_base = damage_instance.value * encounter_scaling
                        poison_damage = max(1, int(damage_base * Config.POISON_SCALING))

                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        current_actor.id,
                        current_actor.id,
                        StatusEffectType.POISON,
                        poison_damage,
                        damage_display,
                        None,
                        CombatEventType.STATUS_EFFECT_OUTCOME,
                    )
                    await self.controller.dispatch_event(event)

                    value = damage_display

            outcomes[effect_type] = StatusEffectOutcome(
                value,
                modifier,
                crit_chance,
                crit_chance_modifier,
                initiative,
                info,
                None,
            )

        embed_data = await self.get_status_effect_outcome_info(
            StatusEffectTrigger.POST_ATTACK, context, actor, outcomes
        )

        return (
            self.combine_outcomes(outcomes.values(), embed_data),
            applied_status_effects,
        )

    async def handle_round_status_effects(
        self,
        context: EncounterContext,
        trigger: StatusEffectTrigger,
    ) -> dict[int, StatusEffectOutcome]:
        actor_outcomes = {}
        for active_actor in context.current_initiative:

            triggered_status_effects = await self.actor_trigger(
                context, active_actor, trigger
            )

            if len(triggered_status_effects) <= 0:
                continue

            outcomes = await self.get_status_effect_outcomes(
                trigger, context, active_actor, triggered_status_effects
            )
            embed_data = await self.get_status_effect_outcome_info(
                trigger, context, active_actor, outcomes
            )
            actor_outcomes[active_actor.id] = self.combine_outcomes(
                outcomes.values(), embed_data
            )

        return actor_outcomes

    async def handle_turn_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        trigger: StatusEffectTrigger,
    ) -> StatusEffectOutcome:
        for active_actor in context.current_initiative:
            if active_actor.id == actor.id:
                actor = active_actor

        if actor.defeated or actor.leaving or actor.is_out:
            return StatusEffectOutcome.EMPTY()

        triggered_status_effects = await self.actor_trigger(context, actor, trigger)

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            trigger, context, actor, triggered_status_effects
        )
        embed_data = await self.get_status_effect_outcome_info(
            trigger, context, actor, outcomes
        )

        return self.combine_outcomes(outcomes.values(), embed_data)

    async def handle_applicant_turn_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> dict[int, StatusEffectOutcome]:
        actor_outcomes = {}

        for active_actor in context.current_initiative:

            triggered_status_effects = await self.actor_trigger(
                context,
                active_actor,
                StatusEffectTrigger.END_OF_APPLICANT_TURN,
            )

            if len(triggered_status_effects) <= 0:
                continue

            outcomes = await self.get_status_effect_outcomes(
                StatusEffectTrigger.END_OF_APPLICANT_TURN,
                context,
                active_actor,
                triggered_status_effects,
            )
            embed_data = await self.get_status_effect_outcome_info(
                StatusEffectTrigger.END_OF_APPLICANT_TURN,
                context,
                active_actor,
                outcomes,
            )
            actor_outcomes[active_actor.id] = self.combine_outcomes(
                outcomes.values(), embed_data
            )

        return actor_outcomes

    async def actor_trigger(
        self,
        context: EncounterContext,
        actor: Actor,
        trigger: StatusEffectTrigger,
    ) -> list[ActiveStatusEffect]:
        triggered = []

        for active_status_effect in actor.status_effects:
            if active_status_effect.remaining_stacks <= 0:
                continue

            status_effect = active_status_effect.status_effect
            status_effect_event = active_status_effect.event

            next_round = status_effect_event.id <= context.round_event_id_cutoff

            delay_consume = status_effect.delay_consume and not next_round
            delay_trigger = status_effect.delay_trigger and not next_round

            actor_is_source = status_effect_event.source_id == actor.id

            if status_effect.delay_for_source_only and not actor_is_source:
                delay_consume = False
                delay_trigger = False

            if not delay_consume and trigger in status_effect.consumed:
                await self.consume_status_stack(context, active_status_effect)

            if not delay_trigger and trigger in status_effect.trigger:
                triggered.append(active_status_effect)

        triggered = sorted(
            triggered, key=lambda item: item.status_effect.priority, reverse=True
        )
        return triggered
