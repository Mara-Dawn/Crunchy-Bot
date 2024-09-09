import datetime
import random

from discord.ext import commands

from combat.actors import Actor, Character, Opponent
from combat.encounter import EncounterContext
from combat.skills.skill import Skill
from combat.skills.status_effect import (
    ActiveStatusEffect,
)
from combat.skills.status_effects import *  # noqa: F403
from combat.skills.types import (
    SkillEffect,
    SkillInstance,
    SkillType,
    StatusEffectOutcome,
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
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
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

    async def apply_status(
        self,
        context: EncounterContext,
        source: Actor,
        target: Actor,
        type: StatusEffectType,
        stacks: int,
        application_value: float = None,
    ):
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

            chance_for_positive = 0.15
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
            return

        for active_actor in context.get_current_initiative():
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
                        return
                    base_value = application_value * Config.BLEED_SCALING

                damage = base_value
            case (
                StatusEffectType.INSPIRED
                | StatusEffectType.HEAL_OVER_TIME
                | StatusEffectType.EVASIVE
                | StatusEffectType.PROTECTION
            ):
                damage = application_value

        if (
            StatusEffectTrigger.END_OF_TURN in status_effect.consumed
            and source.id == target.id
            # and status_effect.delay_to_next_turn
        ):
            stacks += 1

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
                        force=True,
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

    async def consume_status_stack(
        self,
        context: EncounterContext,
        status_effect: ActiveStatusEffect,
        amount: int = 1,
        force: bool = False,
    ):
        status_effect_event = status_effect.event
        if (
            not force
            and status_effect.status_effect.delay
            and status_effect_event.id > context.get_current_round_event_id_cutoff()
        ):
            return
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
                status_effect.delay
                and active_status_effect.event.id
                > context.get_current_round_event_id_cutoff()
            ):
                continue

            if StatusEffectTrigger.ATTRIBUTE in status_effect.trigger:
                triggered_status_effects.append(active_status_effect)

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            None, actor, triggered_status_effects
        )

        combined = self.combine_outcomes(outcomes.values(), None)

        return combined

    async def get_status_effect_outcomes(
        self,
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
                            message = "Bleed was cleansed."
                        if status.status_effect.effect_type == StatusEffectType.POISON:
                            await self.consume_status_stack(
                                context,
                                status,
                                status.remaining_stacks,
                            )
                            message = "Poison was cleansed."
                        if message != "" and message not in info:
                            info.append(message)
                    info = "\n".join(info) if len(info) > 0 else None
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
                    roll = random.random()
                    miss_chance = Config.BLIND_MISS_CHANCE

                    if actor.is_enemy and actor.enemy.is_boss:
                        blind_count = context.get_applied_status_count(
                            actor.id, StatusEffectType.BLIND
                        )
                        miss_chance *= pow(
                            Config.BLIND_DIMINISHING_RETURNS, max(0, blind_count - 1)
                        )

                    modifier = 0 if roll < miss_chance else 1
                case StatusEffectType.EVASIVE:
                    if skill is not None and not skill.base_skill.modifiable:
                        continue
                    chance_to_evade = active_status_effect.event.value / 100
                    roll = random.random()
                    modifier = 0 if roll < chance_to_evade else 1
                case StatusEffectType.FLUSTERED:
                    modifier = 0
                case StatusEffectType.SIMP:
                    modifier = 0.5
                case StatusEffectType.FROST:
                    initiative = -Config.FROST_PENALTY
                    if effect_type not in effect_data:
                        initiative = -Config.FROST_PENALTY
                    else:
                        initiative += -Config.FROST_PENALTY
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
                case StatusEffectType.INSPIRED:
                    modifier = 1 + (active_status_effect.event.value / 100)
                case StatusEffectType.ZONED_IN:
                    crit_chance = 1
                case StatusEffectType.PROTECTION:
                    modifier = 1 - (active_status_effect.event.value / 100)
                case StatusEffectType.FEAR:
                    if skill is not None and skill.type == SkillType.FEASTING:
                        modifier = 1 + (active_status_effect.remaining_stacks * 0.2)
                        await self.consume_status_stack(
                            context,
                            active_status_effect,
                            active_status_effect.remaining_stacks,
                        )
                case StatusEffectType.HIGH:
                    modifier = 0.5 + random.random()
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
                    current_hp = await self.actor_manager.get_actor_current_hp(
                        actor, context.combat_events
                    )
                    remaining_health = current_hp / context.encounter.max_hp
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
        context: EncounterContext,
        actor: Actor,
        effect_data: dict[StatusEffectType, StatusEffectOutcome],
    ) -> dict[str, str] | None:
        outcome_info = {}
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
                case StatusEffectType.POISON:
                    description = f"{actor.name} suffers {outcome.value} poison damage."
                case StatusEffectType.BLIND:
                    if outcome.modifier != 0:
                        continue
                    description = f"{actor.name} misses their attack!"
                case StatusEffectType.EVASIVE:
                    if outcome.modifier != 0:
                        continue
                    title = f"{status_effect.emoji} Miss"
                    description = f"{actor.name} dodged the attack!"
                case StatusEffectType.FLUSTERED:
                    description = f"{actor.name} cannot harm their opponent!"
                case StatusEffectType.SIMP:
                    description = f"{actor.name}'s attacks are half as effective!"
                case StatusEffectType.FEAR:
                    description = f"{actor.name}'s fear increases their damage taken."
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
                outcome_info[title] = description

        if len(outcome_info) <= 0:
            return None
        return outcome_info

    def combine_outcomes(
        self, outcomes: list[StatusEffectOutcome], embed_data: list[str, str] | None
    ) -> StatusEffectOutcome:
        value = None
        modifier = None
        crit_chance = None
        crit_chance_modifier = None
        info = None
        initiative = None

        for outcome in outcomes:
            if outcome.value is not None:
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
            embed_data,
        )

    async def handle_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        status_effects: list[ActiveStatusEffect],
    ) -> StatusEffectOutcome:
        outcomes = await self.get_status_effect_outcomes(context, actor, status_effects)
        embed_data = await self.get_status_effect_outcome_info(context, actor, outcomes)
        return self.combine_outcomes(outcomes.values(), embed_data)

    async def handle_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        skill: Skill,
    ) -> StatusEffectOutcome:
        skill_effect = skill.base_skill.skill_effect

        for active_actor in context.get_current_initiative():
            if active_actor.id == actor.id:
                actor = active_actor

        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_ATTACK
        )

        if len(triggered_status_effects) <= 0 or skill_effect in [
            SkillEffect.NOTHING,
            SkillEffect.HEALING,
        ]:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            context, actor, triggered_status_effects, skill=skill
        )

        embed_data = await self.get_status_effect_outcome_info(context, actor, outcomes)

        combined = self.combine_outcomes(outcomes.values(), embed_data)

        if not skill.base_skill.modifiable:
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

        for active_actor in context.get_current_initiative():
            if active_actor.id == actor.id:
                actor = active_actor

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
            context, actor, triggered_status_effects, skill=skill
        )

        embed_data = await self.get_status_effect_outcome_info(context, actor, outcomes)

        combined = self.combine_outcomes(outcomes.values(), embed_data)

        if not skill.base_skill.modifiable:
            combined.modifier = max(1, combined.modifier)
            combined.crit_chance = None
            combined.crit_chance_modifier = None

        return combined

    async def handle_on_death_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
    ) -> StatusEffectOutcome:
        for active_actor in context.get_current_initiative():
            if active_actor.id == actor.id:
                actor = active_actor

        triggered_status_effects = await self.actor_trigger(
            context, actor, StatusEffectTrigger.ON_DEATH
        )

        if len(triggered_status_effects) <= 0:
            return StatusEffectOutcome.EMPTY()

        outcomes = await self.get_status_effect_outcomes(
            context, actor, triggered_status_effects
        )

        embed_data = await self.get_status_effect_outcome_info(context, actor, outcomes)
        return self.combine_outcomes(outcomes.values(), embed_data)

    async def handle_post_attack_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        target: Actor,
        skill: Skill,
        damage_instance: SkillInstance,
    ) -> StatusEffectOutcome:
        current_actor = context.get_actor(actor.id)
        current_target = context.get_actor(target.id)
        outcomes: dict[StatusEffectType, StatusEffectOutcome] = {}
        triggered_status_effects = await self.actor_trigger(
            context, current_actor, StatusEffectTrigger.POST_ATTACK
        )

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

                    await self.apply_status(
                        context,
                        current_actor,
                        current_target,
                        StatusEffectType.BLEED,
                        3,
                        damage,
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

                    damage = max(1, int(damage_instance.value * Config.POISON_SCALING))
                    if actor.is_enemy:
                        damage_base = damage_instance.scaled_value
                        damage_display = int(damage_base * Config.POISON_SCALING)

                    event = CombatEvent(
                        datetime.datetime.now(),
                        context.encounter.guild_id,
                        context.encounter.id,
                        current_actor.id,
                        current_actor.id,
                        StatusEffectType.POISON,
                        damage,
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

        embed_data = await self.get_status_effect_outcome_info(context, actor, outcomes)

        return self.combine_outcomes(outcomes.values(), embed_data)

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
