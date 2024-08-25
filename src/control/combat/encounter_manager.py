import asyncio
import datetime
import importlib
import random

import discord
from discord.ext import commands

from combat.actors import Actor, Character
from combat.encounter import Encounter, EncounterContext, TurnData
from combat.enemies import *  # noqa: F403
from combat.enemies.enemy import Enemy
from combat.enemies.types import EnemyType
from combat.gear.types import Base
from combat.skills.skill import CharacterSkill, Skill
from combat.skills.types import (
    SkillEffect,
    SkillInstance,
    StatusEffectApplication,
    StatusEffectTrigger,
)
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.context_loader import ContextLoader
from control.combat.object_factory import ObjectFactory
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from control.types import ControllerModuleMap, UserSetting
from datalayer.database import Database
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.inventory_event import InventoryEvent
from events.types import (
    BeansEventType,
    CombatEventType,
    EncounterEventType,
    EventType,
    UIEventType,
)
from events.ui_event import UIEvent
from items.types import ItemType
from view.combat.combat_turn_view import CombatTurnView
from view.combat.embed import EnemyOverviewEmbed
from view.combat.engage_view import EnemyEngageView
from view.combat.grace_period import GracePeriodView
from view.combat.leave_view import EncounterLeaveView
from view.combat.special_drop import SpecialDropView


class EncounterManager(Service):

    BOSS_TYPE = {
        3: EnemyType.DADDY_P1,
        6: EnemyType.WEEB_BALL,
        # 9: None,
        # 12: None,
    }
    BOSS_LEVEL = {v: k for k, v in BOSS_TYPE.items()}
    BOSS_KEY = {
        3: ItemType.DADDY_KEY,
        6: ItemType.WEEB_KEY,
        9: None,
        12: None,
    }

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.skill_manager: CombatSkillManager = self.controller.get_service(
            CombatSkillManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.gear_manager: CombatGearManager = self.controller.get_service(
            CombatGearManager
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )
        self.context_loader: ContextLoader = self.controller.get_service(ContextLoader)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.log_name = "Encounter"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.NEW_ROUND:
                        await self.refresh_encounter_thread(
                            encounter_event.encounter_id
                        )
                    case EncounterEventType.INITIATE:
                        await self.initiate_encounter(encounter_event.encounter_id)
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.add_member_to_encounter(
                            encounter_event.encounter_id, encounter_event.member_id
                        )
                    case EncounterEventType.END:
                        await self.update_guild_status(event.guild_id)

            case EventType.COMBAT:
                combat_event: CombatEvent = event
                if not event.synchronized:
                    return
                if combat_event.combat_event_type in [
                    CombatEventType.MEMBER_TURN,
                    CombatEventType.ENEMY_TURN,
                ]:
                    await self.skill_manager.trigger_special_skill_effects(event)
                    context = await self.context_loader.load_encounter_context(
                        combat_event.encounter_id
                    )
                    if await self.context_needs_update_check(context):
                        return
                    await self.refresh_round_overview(context)
                if combat_event.combat_event_type not in [
                    CombatEventType.ENEMY_END_TURN,
                    CombatEventType.MEMBER_END_TURN,
                ]:
                    return
                await self.refresh_encounter_thread(combat_event.encounter_id)

    async def get_random_enemy(
        self, encounter_level: int, exclude: list[EnemyType] = None
    ) -> Enemy:
        if exclude is None:
            exclude = []

        enemies = [await self.factory.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy
            for enemy in enemies
            if encounter_level >= enemy.min_level
            and encounter_level <= enemy.max_level
            and not enemy.is_boss
            and enemy.type not in exclude
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        # spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        return enemy

    async def create_encounter(
        self, guild_id: int, enemy_type: EnemyType = None, level: int = None
    ):
        max_encounter_level = await self.database.get_guild_level(guild_id)
        min_encounter_level = max(
            1, int(max_encounter_level * Config.ENCOUNTER_MIN_LVL_SCALING)
        )

        if level is not None:
            encounter_level = min(max_encounter_level, level)
        else:
            encounter_level = random.randint(min_encounter_level, max_encounter_level)

        if enemy_type is not None:
            enemy = await self.factory.get_enemy(enemy_type)
            if not (
                encounter_level >= enemy.min_level
                and encounter_level <= enemy.max_level
            ):
                raise TypeError
        else:
            enemy = await self.get_random_enemy(encounter_level)

        effective_encounter_level = encounter_level
        if enemy.is_boss:
            effective_encounter_level += 1

        roll = random.uniform(0.95, 1.05)
        enemy_health = (
            enemy.health
            * Config.ENEMY_HEALTH_SCALING[effective_encounter_level]
            * Config.AVERAGE_PLAYER_POTENCY[effective_encounter_level]
        )
        enemy_health *= pow(
            Config.ENEMY_HEALTH_LVL_FALLOFF, (encounter_level - enemy.min_level)
        )
        enemy_health *= roll

        return Encounter(guild_id, enemy.type, encounter_level, enemy_health)

    async def spawn_encounter(
        self,
        guild: discord.Guild,
        channel_id: int,
        enemy_type: EnemyType = None,
        level: int = None,
    ):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(
            guild.id, enemy_type=enemy_type, level=level
        )

        enemy = await self.factory.get_enemy(encounter.enemy_type)
        view = EnemyEngageView(self.controller, enemy)
        channel = guild.get_channel(channel_id)

        spawn_pings = ""
        ping_role = await self.settings_manager.get_spawn_ping_role(guild.id)
        if ping_role is not None:
            spawn_pings += f"<@&{ping_role}>"

        guild_level = await self.database.get_guild_level(encounter.guild_id)
        if encounter.enemy_level == guild_level:
            max_lvl_ping_role = await self.settings_manager.get_max_lvl_spawn_ping_role(
                guild.id
            )
            if max_lvl_ping_role is not None:
                spawn_pings += f"<@&{max_lvl_ping_role}>"

        message = await self.context_loader.send_message(
            channel, content=spawn_pings, view=view
        )

        encounter.message_id = message.id
        encounter.channel_id = message.channel.id

        encounter_id = await self.database.log_encounter(encounter)

        view.set_message(message)
        encounter.id = encounter_id

        if encounter.enemy_type == EnemyType.MIMIC:
            mock_enemy = await self.get_random_enemy(
                encounter.enemy_level, exclude=[EnemyType.MIMIC]
            )
            mock_encounter = Encounter(
                guild.id, mock_enemy.type, encounter.enemy_level, encounter.max_hp
            )
            embed = await self.embed_manager.get_spawn_embed(mock_encounter)
        else:
            embed = await self.embed_manager.get_spawn_embed(encounter)

        await view.refresh_ui(embed=embed, encounter_id=encounter_id)

        event = EncounterEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            EncounterEventType.SPAWN,
        )
        await self.controller.dispatch_event(event)

    async def apply_late_join_penalty(self, encounter_id: int, member_id: int) -> str:
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        status_effects = await self.database.get_status_effects_by_encounter(
            encounter_id
        )
        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter,
            encounter_events,
            combat_events,
            status_effects,
        )

        max_enemy_hp = encounter.max_hp
        current_enemy_hp = await self.actor_manager.get_actor_current_hp(
            opponent, combat_events
        )

        combat_progress = current_enemy_hp / max_enemy_hp

        if combat_progress >= 0.5:
            return ""

        if combat_progress < 0.5:
            additional_message = "You joined late, so you will get a 50% loot penalty."
            event = EncounterEvent(
                datetime.datetime.now(),
                encounter.guild_id,
                encounter.id,
                member_id,
                EncounterEventType.PENALTY50,
            )
            await self.controller.dispatch_event(event)
        elif combat_progress <= 0.25:
            additional_message = "You joined late, so you will get a 75% loot penalty."
            event = EncounterEvent(
                datetime.datetime.now(),
                encounter.guild_id,
                encounter.id,
                member_id,
                EncounterEventType.PENALTY75,
            )
            await self.controller.dispatch_event(event)

        return additional_message

    async def create_encounter_thread(self, encounter: Encounter) -> discord.Thread:
        channel = self.bot.get_channel(encounter.channel_id)
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        thread = await channel.create_thread(
            name=f"Encounter: {enemy.name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60,
        )

        await self.database.log_encounter_thread(
            encounter.id, thread.id, encounter.guild_id, encounter.channel_id
        )

        return thread

    async def add_member_to_encounter(self, encounter_id: int, member_id: int):
        thread_id = await self.database.get_encounter_thread(encounter_id)

        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread = None
        initiate_combat = False
        new_thread = False
        additional_message = ""

        if thread_id is None:
            thread = await self.create_encounter_thread(encounter)
            initiate_combat = True
            new_thread = True
        else:
            thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)
            additional_message = await self.apply_late_join_penalty(
                encounter_id, member_id
            )

        if thread is None:
            return

        enemy = await self.factory.get_enemy(encounter.enemy_type)

        min_participants = enemy.min_encounter_scale
        guild_level = await self.database.get_guild_level(encounter.guild_id)

        if encounter.enemy_level == guild_level:
            min_participants = max(
                min_participants,
                int(enemy.max_players * Config.ENCOUNTER_MAX_LVL_SIZE_SCALING),
            )

        if min_participants > 1:
            initiate_combat = False
            participants = (
                await self.database.get_encounter_participants_by_encounter_id(
                    encounter.id
                )
            )
            if len(participants) == min_participants:
                initiate_combat = True

        if new_thread and not initiate_combat:
            wait_embed = await self.embed_manager.get_waiting_for_party_embed(
                min_participants
            )
            if not enemy.is_boss:
                leave_view = EncounterLeaveView(self.controller)
            message = await self.context_loader.send_message(
                thread, content="", embed=wait_embed, view=leave_view
            )

        if initiate_combat:
            wait_time = Config.COMBAT_INITIAL_WAIT
            round_embed = await self.embed_manager.get_initiation_embed(wait_time)
            # will trigger the combat start on expiration
            view = GracePeriodView(self.controller, encounter, wait_time)
            message = await self.context_loader.send_message(
                thread, content="", embed=round_embed, view=view
            )
            view.set_message(message)

        user = self.bot.get_guild(encounter.guild_id).get_member(member_id)
        await thread.add_user(user)

        embed = self.embed_manager.get_actor_join_embed(
            user, additional_message=additional_message
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await self.context_loader.send_message(thread, content="", embed=embed)

        encounters = await self.database.get_encounter_participants(encounter.guild_id)
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        max_encounter_size = enemy.max_players
        if encounter.id not in encounters:
            # TODO why does this happen
            return
        if len(encounters[encounter.id]) >= max_encounter_size and not enemy.is_boss:
            event = UIEvent(UIEventType.COMBAT_FULL, encounter.id)
            await self.controller.dispatch_ui_event(event)

    async def skip_turn(
        self,
        actor: Actor,
        context: EncounterContext,
        reason: str = None,
        timeout: bool = False,
        silent: bool = False,
    ):
        if not silent:
            if reason is None:
                reason = ""
            embed = self.embed_manager.get_turn_skip_embed(actor, reason, context)
            await self.context_loader.append_embed_to_round(context, embed)

        combat_event_type = CombatEventType.MEMBER_END_TURN
        if actor.is_enemy:
            combat_event_type = CombatEventType.ENEMY_END_TURN

        if timeout:
            event = CombatEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                actor.id,
                actor.id,
                None,
                None,
                None,
                CombatEventType.MEMBER_TURN_SKIP,
            )
            await self.controller.dispatch_event(event)

        await self.handle_turn_status_effects(
            context, actor, StatusEffectTrigger.END_OF_TURN
        )

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            actor.id,
            actor.id,
            None,
            None,
            None,
            combat_event_type,
        )
        await self.controller.dispatch_event(event)

    async def opponent_turn(self, context: EncounterContext):
        opponent = context.opponent

        if context.is_concluded():
            await self.refresh_encounter_thread(context.encounter.id)
            return

        controller_type = opponent.enemy.controller
        controller_class = getattr(
            importlib.import_module(
                "control.combat.enemy."
                + ControllerModuleMap.get_module(controller_type)
            ),
            controller_type,
        )
        enemy_controller = self.controller.get_service(controller_class)

        await enemy_controller.handle_turn(context)

        await self.handle_turn_status_effects(
            context, opponent, StatusEffectTrigger.END_OF_TURN
        )

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            None,
            None,
            None,
            None,
            CombatEventType.ENEMY_END_TURN,
        )
        await self.controller.dispatch_event(event)

    async def handle_round_status_effects(
        self,
        context: EncounterContext,
        trigger: StatusEffectTrigger,
    ):
        context = await self.context_loader.load_encounter_context(context.encounter.id)

        for active_actor in context.get_current_initiative():

            triggered_status_effects = await self.status_effect_manager.actor_trigger(
                context, active_actor, trigger
            )

            if len(triggered_status_effects) <= 0:
                continue

            effect_data = await self.status_effect_manager.handle_status_effects(
                context, active_actor, triggered_status_effects
            )

            if len(effect_data) > 0:
                status_effect_embed = self.embed_manager.get_status_effect_embed(
                    active_actor, effect_data
                )
                await self.context_loader.append_embed_to_round(
                    context, status_effect_embed
                )

    async def handle_turn_status_effects(
        self,
        context: EncounterContext,
        actor: Actor,
        trigger: StatusEffectTrigger,
    ):
        context = await self.context_loader.load_encounter_context(context.encounter.id)

        for active_actor in context.get_current_initiative():
            if active_actor.id == actor.id:
                actor = active_actor

        if actor.defeated or actor.leaving or actor.is_out:
            return context

        triggered_status_effects = await self.status_effect_manager.actor_trigger(
            context, actor, trigger
        )

        if len(triggered_status_effects) <= 0:
            return context

        effect_data = await self.status_effect_manager.handle_status_effects(
            context, actor, triggered_status_effects
        )

        if len(effect_data) > 0:
            status_effect_embed = self.embed_manager.get_status_effect_embed(
                actor, effect_data
            )
            await self.context_loader.append_embed_to_round(
                context, status_effect_embed
            )

        context = await self.context_loader.load_encounter_context(context.encounter.id)

        return context

    async def calculate_character_aoe_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        available_targets: list[Actor],
    ) -> tuple[list[tuple[Actor, SkillInstance, float], discord.Embed]]:
        damage_data = []
        embed_data = {}
        effect_modifier, post_embed_data = (
            await self.status_effect_manager.handle_attack_status_effects(
                context, source, skill
            )
        )
        if post_embed_data is not None:
            embed_data = embed_data | post_embed_data

        for target in available_targets:
            instances = await self.skill_manager.get_skill_effect(
                source, skill, combatant_count=context.get_combat_scale()
            )
            instance = instances[0]
            instance.apply_effect_modifier(effect_modifier)

            current_hp = await self.actor_manager.get_actor_current_hp(
                target, context.combat_events
            )

            on_damage_effect_modifier, post_embed_data = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )

            if post_embed_data is not None:
                embed_data = embed_data | post_embed_data

            instance.apply_effect_modifier(on_damage_effect_modifier)

            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            if skill.base_skill.skill_effect == SkillEffect.HEALING:
                total_damage *= -1

            new_target_hp = min(max(0, current_hp - total_damage), target.max_hp)

            damage_data.append((target, instance, new_target_hp))
        return damage_data, embed_data

    async def calculate_character_skill(
        self,
        context: EncounterContext,
        skill: Skill,
        source: Character,
        target: Actor,
    ) -> tuple[list[tuple[Actor, SkillInstance, float], list[discord.Embed]]]:
        skill_instances = await self.skill_manager.get_skill_effect(
            source, skill, combatant_count=context.get_combat_scale()
        )

        skill_value_data = []
        hp_cache = {}
        embed_data = {}

        for instance in skill_instances:
            effect_modifier, post_embed_data = (
                await self.status_effect_manager.handle_attack_status_effects(
                    context,
                    source,
                    skill,
                )
            )
            if post_embed_data is not None:
                embed_data = embed_data | post_embed_data

            instance.apply_effect_modifier(effect_modifier)

            effect_modifier, post_embed_data = (
                await self.status_effect_manager.handle_on_damage_taken_status_effects(
                    context,
                    target,
                    skill,
                )
            )

            if post_embed_data is not None:
                embed_data = embed_data | post_embed_data

            instance.apply_effect_modifier(effect_modifier)

            total_skill_value = await self.actor_manager.get_skill_damage_after_defense(
                target, skill, instance.scaled_value
            )

            target_id = target.id
            if target_id is None:
                target_id = -1

            if target_id not in hp_cache:
                hp_cache[target_id] = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )

            current_hp = hp_cache[target_id]

            if skill.base_skill.skill_effect != SkillEffect.HEALING:
                total_skill_value *= -1

            new_target_hp = min(max(0, current_hp + total_skill_value), target.max_hp)
            hp_cache[target_id] = new_target_hp

            skill_value_data.append((target, instance, new_target_hp))

        return skill_value_data, embed_data

    async def combatant_turn(
        self,
        context: EncounterContext,
        character: Character,
        skill_data: CharacterSkill,
        target: Actor = None,
    ):
        if context.is_concluded():
            await self.refresh_encounter_thread(context.encounter.id)
            return

        if target is None:
            target = await self.skill_manager.get_character_default_target(
                character, skill_data.skill, context
            )

        if target is not None:
            if skill_data.skill.base_skill.aoe:
                # assumes party targeted
                damage_data, post_embed_data = await self.calculate_character_aoe_skill(
                    context,
                    skill_data.skill,
                    character,
                    context.get_active_combatants(),
                )
            else:
                damage_data, post_embed_data = await self.calculate_character_skill(
                    context, skill_data.skill, character, target
                )

            turn = TurnData(
                actor=character,
                skill=skill_data.skill,
                damage_data=damage_data,
                post_embed_data=post_embed_data,
            )
        else:
            turn = TurnData(
                actor=character,
                skill=skill_data.skill,
                damage_data=[],
                post_embed_data={"No Target": "The Skill had no effect."},
            )

        await self.context_loader.append_embed_generator_to_round(
            context, self.embed_manager.handle_actor_turn_embed(turn, context)
        )

        if turn.post_embed_data is not None:
            await self.context_loader.append_embeds_to_round(
                context, character, turn.post_embed_data
            )

        for target, damage_instance, _ in turn.damage_data:
            total_damage = await self.actor_manager.get_skill_damage_after_defense(
                target, turn.skill, damage_instance.scaled_value
            )

            embed_data = (
                await self.status_effect_manager.handle_post_attack_status_effects(
                    context,
                    character,
                    target,
                    skill_data.skill,
                    damage_instance,
                )
            )
            if embed_data is not None:
                await self.context_loader.append_embeds_to_round(
                    context, character, embed_data
                )

            status_effect_damage = (
                await self.actor_manager.get_skill_damage_after_defense(
                    target, turn.skill, damage_instance.value
                )
            )
            for skill_status_effect in turn.skill.base_skill.status_effects:
                application_value = None
                match skill_status_effect.application:
                    case StatusEffectApplication.ATTACK_VALUE:
                        if skill_data.skill.base_skill.skill_effect == SkillEffect.BUFF:
                            application_value = damage_instance.skill_base
                        else:
                            application_value = status_effect_damage
                    case StatusEffectApplication.MANUAL_VALUE:
                        application_value = skill_status_effect.application_value
                    case StatusEffectApplication.DEFAULT:
                        if status_effect_damage <= 0:
                            application_value = status_effect_damage

                status_effect_target = target
                if skill_status_effect.self_target:
                    status_effect_target = character

                if random.random() < skill_status_effect.application_chance:
                    await self.status_effect_manager.apply_status(
                        context,
                        character,
                        status_effect_target,
                        skill_status_effect.status_effect_type,
                        skill_status_effect.stacks,
                        application_value,
                    )

            event = CombatEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                character.id,
                target.id,
                skill_data.skill.base_skill.skill_type,
                total_damage,
                skill_data.skill.id,
                CombatEventType.MEMBER_TURN,
            )
            await self.controller.dispatch_event(event)

        await self.handle_turn_status_effects(
            context, character, StatusEffectTrigger.END_OF_TURN
        )

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            character.id,
            None,
            None,
            None,
            None,
            CombatEventType.MEMBER_END_TURN,
        )
        await self.controller.dispatch_event(event)

    async def combatant_timeout(
        self,
        context: EncounterContext,
        character: Character,
    ):
        timeout_count = context.get_timeout_count(character.id)
        message = (
            f"{character.name} was inactive for too long, their turn will be skipped."
        )
        timeout_count += 1

        jail_time = Config.TIMEOUT_JAIL_TIME
        jail_message = (
            f"<@{character.member.id}> was jailed for missing their turn in combat."
        )

        if (
            timeout_count >= Config.TIMEOUT_COUNT_LIMIT
            and not context.opponent.enemy.is_boss
        ):
            event = EncounterEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                character.id,
                EncounterEventType.MEMBER_OUT,
            )
            await self.controller.dispatch_event(event)
            message += f" They reached {Config.TIMEOUT_COUNT_LIMIT} total timeouts and will be excluded from the fight."
            jail_time += Config.KICK_JAIL_TIME
            jail_message = f"<@{character.member.id}> was jailed for repeatedly missing their turn in combat, leading to them getting kicked."

        await self.skip_turn(character, context, message, timeout=True)
        await self.jail_manager.jail_or_extend_user(
            context.encounter.guild_id,
            self.bot.user.id,
            character.member,
            jail_time,
            jail_message,
        )

    async def conclude_encounter(self, context: EncounterContext, success: bool = True):

        if success:
            embed = await self.embed_manager.get_combat_success_embed(context)
        else:
            embed = await self.embed_manager.get_combat_failed_embed(context)

        await self.context_loader.send_message(context.thread, content="", embed=embed)

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            self.bot.user.id,
            EncounterEventType.END,
        )
        await self.controller.dispatch_event(event)

        if success:
            await self.payout_loot(context)

    async def payout_loot(self, context: EncounterContext):
        loot = await self.gear_manager.roll_enemy_loot(context)

        now = datetime.datetime.now()

        for member, member_loot in loot.items():

            await asyncio.sleep(1)
            beans = member_loot[0]
            embeds = []
            loot_head_embed = await self.embed_manager.get_loot_embed(member, beans)
            embeds.append(loot_head_embed)

            message = await self.context_loader.send_message(
                context.thread, content=f"<@{member.id}>", embeds=embeds
            )

            event = BeansEvent(
                now,
                member.guild.id,
                BeansEventType.COMBAT_LOOT,
                member.id,
                beans,
            )
            await self.controller.dispatch_event(event)

            auto_scrap = await self.database.get_user_setting(
                member.id, context.encounter.guild_id, UserSetting.AUTO_SCRAP
            )
            if auto_scrap is None:
                auto_scrap = 0
            auto_scrap = int(auto_scrap)

            gear_to_scrap = []
            for drop in member_loot[1]:
                if drop.level <= auto_scrap and drop.base.base_type != Base.SKILL:
                    gear_to_scrap.append(drop)
                    continue
                embeds.append(drop.get_embed())
                await asyncio.sleep(1)
                await self.context_loader.edit_message(message, embeds=embeds)

            if len(gear_to_scrap) > 0:
                total_scrap = await self.gear_manager.scrap_gear(
                    member.id, context.encounter.guild_id, gear_to_scrap
                )
                scrap_embed = await self.embed_manager.get_loot_scrap_embed(
                    member, total_scrap, auto_scrap
                )
                embeds.append(scrap_embed)
                await self.context_loader.edit_message(message, embeds=embeds)

            item = member_loot[2]

            if item is not None:
                item = await self.item_manager.give_item(
                    member.guild.id, member.id, item
                )
                embeds.append(item.get_embed(self.bot, show_price=False))
                await asyncio.sleep(1)

                await self.context_loader.edit_message(message, embeds=embeds)

        if await self.drop_boss_key_check(context):
            item_type = self.BOSS_KEY[context.encounter.enemy_level]
            if item_type is None:
                return
            item = await self.item_manager.get_item(context.thread.guild.id, item_type)
            view = SpecialDropView(
                self.controller,
                context.encounter.id,
                item,
                delay=Config.BOSS_KEY_CLAIM_DELAY,
            )
            embed = self.embed_manager.get_special_item_embed(
                item, delay_claim=Config.BOSS_KEY_CLAIM_DELAY
            )
            message = await self.context_loader.send_message(
                context.thread, embed=embed, view=view
            )
            view.set_message(message)

    async def drop_boss_key_check(self, context: EncounterContext) -> bool:
        guild = context.thread.guild
        guild_level = await self.database.get_guild_level(guild.id)

        if context.encounter.enemy_level != guild_level:
            return False
        if guild_level not in Config.BOSS_LEVELS:
            return False

        requirement = Config.LEVEL_REQUIREMENTS[guild_level]
        start_event_id = 0

        if (guild_level) in Config.BOSS_LEVELS:
            last_fight_event = await self.database.get_guild_last_boss_attempt(
                guild.id, self.BOSS_TYPE[guild_level]
            )
            if last_fight_event is not None:
                start_event_id = last_fight_event.id
                requirement = Config.BOSS_RETRY_REQUIREMENT

        progress = await self.database.get_guild_level_progress(
            guild.id, guild_level, start_id=start_event_id
        )

        return progress == requirement

    async def context_needs_update_check(self, context: EncounterContext) -> bool:
        already_defeated = [actor.id for actor in context.get_defeated_combatants()]
        update_context = False

        for event in context.encounter_events:
            match event.encounter_event_type:
                case EncounterEventType.ENEMY_DEFEAT:
                    already_defeated.append(event.member_id)

        for actor in context.actors:
            if actor.id in already_defeated:
                continue

            health = await self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )

            if health <= 0:
                update_context = True
                if actor.is_enemy:
                    controller_type = actor.enemy.controller
                    controller_class = getattr(
                        importlib.import_module(
                            "control.combat.enemy."
                            + ControllerModuleMap.get_module(controller_type)
                        ),
                        controller_type,
                    )
                    enemy_controller = self.controller.get_service(controller_class)

                    await enemy_controller.on_defeat(context, actor)
                    continue

                embed_data, prevent_death = (
                    await self.status_effect_manager.handle_on_death_status_effects(
                        context, actor
                    )
                )
                if embed_data is not None:
                    await self.context_loader.append_embeds_to_round(
                        context, actor, embed_data
                    )
                if prevent_death:
                    continue

                encounter_event_type = EncounterEventType.MEMBER_DEFEAT
                embed = self.embed_manager.get_actor_defeated_embed(actor)
                await self.context_loader.send_message(
                    context.thread, content="", embed=embed
                )

                event = EncounterEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    actor.id,
                    encounter_event_type,
                )
                await self.controller.dispatch_event(event)

            if context.new_round() and actor.leaving:
                event = EncounterEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    actor.id,
                    EncounterEventType.MEMBER_OUT,
                )
                await self.controller.dispatch_event(event)
                update_context = True

        return update_context

    async def delete_previous_combat_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None and embed.title is not None:
                    await message.delete()
                    break

    async def get_previous_enemy_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None and embed.title is not None:
                    return message
        return None

    async def initiate_encounter(self, encounter_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        enemy = await self.factory.get_enemy(encounter.enemy_type)
        controller_type = enemy.controller
        controller_class = getattr(
            importlib.import_module(
                "control.combat.enemy."
                + ControllerModuleMap.get_module(controller_type)
            ),
            controller_type,
        )
        enemy_controller = self.controller.get_service(controller_class)
        await enemy_controller.intro(encounter_id)
        await self.refresh_encounter_thread(encounter_id)

    async def refresh_round_overview(self, context: EncounterContext):
        round_message = await self.context_loader.get_previous_turn_message(
            context.thread
        )
        if round_message is not None:
            round_embeds = round_message.embeds
            cont = round_embeds[0].title == "Round Continued.."
            round_embed = await self.embed_manager.get_round_embed(context, cont=cont)
            round_embeds[0] = round_embed
            await self.context_loader.edit_message(
                round_message, embeds=round_embeds, attachments=[]
            )

    async def refresh_encounter_thread(self, encounter_id: int):
        context = await self.context_loader.load_encounter_context(encounter_id)

        if await self.context_needs_update_check(context):
            context = await self.context_loader.load_encounter_context(encounter_id)

        if context.is_concluded():
            return

        if context.opponent.defeated:
            await self.delete_previous_combat_info(context.thread)
            await self.conclude_encounter(context)
            return

        if len(context.get_active_combatants()) <= 0:
            await self.delete_previous_combat_info(context.thread)
            await self.conclude_encounter(context, success=False)
            return

        current_actor = context.get_current_actor()

        if current_actor.id == context.beginning_actor.id and not context.new_round():
            await self.handle_round_status_effects(
                context, StatusEffectTrigger.END_OF_ROUND
            )
            event = EncounterEvent(
                datetime.datetime.now(),
                context.encounter.guild_id,
                context.encounter.id,
                self.bot.user.id,
                EncounterEventType.NEW_ROUND,
            )
            await self.controller.dispatch_event(event)
            return

        if not context.new_round():
            await self.refresh_round_overview(context)

        if not context.new_turn():
            return

        enemy_embed = await self.embed_manager.get_combat_embed(context)

        if context.new_round():
            await self.delete_previous_combat_info(context.thread)
            leave_view = None
            if not context.opponent.enemy.is_boss:
                leave_view = EncounterLeaveView(self.controller)
            message = await self.context_loader.send_message(
                context.thread, content="", embed=enemy_embed, view=leave_view
            )
            if not context.opponent.enemy.is_boss:
                leave_view.set_message(message)
            round_embed = await self.embed_manager.get_round_embed(context)
            await self.context_loader.send_message(
                context.thread, content="", embed=round_embed
            )
        else:
            message = await self.get_previous_enemy_info(context.thread)
            if message is not None:
                await self.context_loader.edit_message(message, embed=enemy_embed)

        context = await self.handle_turn_status_effects(
            context, current_actor, StatusEffectTrigger.START_OF_TURN
        )
        current_actor = context.get_current_actor()

        if current_actor.force_skip:
            await self.skip_turn(current_actor, context)
            return

        if current_actor.is_enemy:
            await self.opponent_turn(context)
            return

        if current_actor.defeated:
            await self.skip_turn(
                current_actor, context, f"{current_actor.name} is defeated."
            )
            return

        if current_actor.leaving:
            await self.skip_turn(
                current_actor,
                context,
                f"{current_actor.name} has left the encounter and will be removed in the next round.",
            )
            return

        if current_actor.is_out:
            await self.skip_turn(current_actor, context, "", silent=True)
            return

        enemy_embeds = await self.embed_manager.get_character_turn_embeds(context)

        view = await CombatTurnView.create(self.controller, current_actor, context)

        message = await self.context_loader.send_message(
            context.thread,
            content=f"<@{current_actor.id}>",
            embeds=enemy_embeds,
            view=view,
        )
        view.set_message(message)
        return

    async def update_guild_status(self, guild_id: int):
        combat_channels = await self.settings_manager.get_combat_channels(guild_id)
        guild = self.bot.get_guild(guild_id)

        guild_level = await self.database.get_guild_level(guild.id)

        requirement = Config.LEVEL_REQUIREMENTS[guild_level]
        start_event_id = 0

        if (guild_level) in Config.BOSS_LEVELS:
            last_fight_event = await self.database.get_guild_last_boss_attempt(
                guild.id, self.BOSS_TYPE[guild_level]
            )
            if last_fight_event is not None:
                start_event_id = last_fight_event.id
                requirement = Config.BOSS_RETRY_REQUIREMENT

        progress = await self.database.get_guild_level_progress(
            guild.id, guild_level, start_id=start_event_id
        )

        if progress >= requirement and (guild_level) not in Config.BOSS_LEVELS:
            guild_level += 1
            await self.database.set_guild_level(guild.id, guild_level)

            bean_channels = await self.settings_manager.get_beans_notification_channels(
                guild_id
            )
            beans_role_id = await self.settings_manager.get_beans_role(guild_id)
            guild = self.bot.get_guild(guild_id)
            if guild is not None:
                announcement = (
                    "**A new Level has been unlocked!**\n"
                    f"Congratulations! You fulfilled the requirements to reach **Level {guild_level}**.\n"
                    "Good luck facing the challenges ahead, stronger opponents and greater rewards are waiting for you."
                )
                if beans_role_id is not None:
                    announcement += f"\n<@&{beans_role_id}>"

                for channel_id in bean_channels:
                    channel = guild.get_channel(channel_id)
                    if channel is not None:
                        await channel.send(announcement)

        for channel_id in combat_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            await self.refresh_combat_messages(guild_id)

    async def refresh_combat_messages(self, guild_id: int, purge: bool = False):
        combat_channels = await self.settings_manager.get_combat_channels(guild_id)

        guild = self.bot.get_guild(guild_id)

        for channel_id in combat_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue

            guild_level = await self.database.get_guild_level(guild.id)
            requirement = Config.LEVEL_REQUIREMENTS[guild_level]
            start_event_id = 0

            if (guild_level) in Config.BOSS_LEVELS:
                last_fight_event = await self.database.get_guild_last_boss_attempt(
                    guild.id, self.BOSS_TYPE[guild_level]
                )
                if last_fight_event is not None:
                    start_event_id = last_fight_event.id
                    requirement = Config.BOSS_RETRY_REQUIREMENT

            progress = await self.database.get_guild_level_progress(
                guild.id, guild_level, start_id=start_event_id
            )

            start_hour = await self.settings_manager.get_combat_max_lvl_start(guild.id)
            end_hour = await self.settings_manager.get_combat_max_lvl_end(guild.id)

            current_time = datetime.datetime.now()
            current_hour = current_time.hour

            post_start = start_hour <= current_hour
            pre_end = current_hour < end_hour
            enemies_asleep = False
            wakeup = current_time

            if start_hour < end_hour:
                if current_time.weekday in [4, 5] and not pre_end:
                    pre_end = True
                if current_time.weekday in [5, 6] and not post_start:
                    post_start = True
                if not (post_start and pre_end):
                    enemies_asleep = True
            else:
                if current_time.weekday() in [5, 6] and not pre_end:
                    pre_end = True
                if current_time.weekday() in [5, 6] and not post_start:
                    post_start = True
                if not (post_start or pre_end):
                    enemies_asleep = True

            additional_info = None
            if enemies_asleep:
                if current_hour > start_hour:
                    wakeup = current_time + datetime.timedelta(days=1)
                wakeup = wakeup.replace(hour=start_hour, minute=0)
                additional_info = (
                    f"**\nThe enemies of level {guild_level} and above are currently asleep.\n"
                )
                additional_info += f"They will return <t:{int(wakeup.timestamp())}:R> **"

            head_embed = EnemyOverviewEmbed(
                self.bot.user,
                guild_level,
                requirement,
                progress,
                additional_info,
            )

            if purge:
                await channel.purge()
                await self.context_loader.send_message(
                    channel, content="", embed=head_embed
                )
            else:
                async for message in channel.history(limit=100):
                    if message.thread is not None:
                        age_delta = (
                            datetime.datetime.now(datetime.UTC) - message.created_at
                        )
                        if age_delta.total_seconds() > 60 * 60:
                            await message.delete()

                    if len(message.embeds) <= 0:
                        continue

                    embed_title = message.embeds[0].title
                    if embed_title[:16] == "Combat Zone":
                        await self.context_loader.edit_message(
                            message, embed=head_embed
                        )
