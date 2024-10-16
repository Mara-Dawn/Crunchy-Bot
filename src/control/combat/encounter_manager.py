import datetime
import random

import discord
from discord.ext import commands

from combat.actors import Character
from combat.encounter import Encounter, EncounterContext
from combat.enemies import *  # noqa: F403
from combat.enemies.types import EnemyType
from combat.engine.engine import Engine
from combat.engine.types import StateType
from combat.skills.skill import CharacterSkill
from config import Config
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.combat.context_loader import ContextLoader
from control.combat.discord_manager import DiscordManager
from control.combat.object_factory import ObjectFactory
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from control.user_settings_manager import UserSettingsManager
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import (
    CombatEventType,
    EncounterEventType,
    EventType,
)
from items.types import ItemType


class EncounterManager(Service):

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
        self.user_settings_manager: UserSettingsManager = self.controller.get_service(
            UserSettingsManager
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
        self.discord: DiscordManager = self.controller.get_service(DiscordManager)
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.jail_manager: JailManager = self.controller.get_service(JailManager)
        self.log_name = "Encounter"

        self.engine_cache: list[Engine] = []

    async def listen_for_event(self, event: BotEvent):
        if not event.synchronized:
            return
        if event.type not in [
            EventType.ENCOUNTER,
            EventType.COMBAT,
            EventType.STATUS_EFFECT,
        ]:
            return

        removing = []
        for engine in self.engine_cache:
            if engine.done:
                removing.append(engine)
                continue

            if event.encounter_id == engine.context.encounter.id:
                await engine.handle(event)

        for engine in removing:
            if engine in self.engine_cache:
                self.engine_cache.remove(engine)
                self.logger.log(
                    event.guild_id,
                    f"({engine.context.encounter.id}) removing engine from cache. remaining: {len(self.engine_cache)}",
                )

        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.END | EncounterEventType.SPAWN:
                        await self.discord.update_guild_status(event.guild_id)

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
            encounter_level = min(enemy.max_level, encounter_level)
            encounter_level = max(enemy.min_level, encounter_level)
        else:
            enemy = await self.actor_manager.get_random_enemy(encounter_level)

        effective_encounter_level = encounter_level
        if enemy.is_boss:
            effective_encounter_level += 1

        roll = random.uniform(0.95, 1.05)
        enemy_health = (
            enemy.health
            * Config.ENEMY_HEALTH_SCALING[effective_encounter_level]
            * Config.AVERAGE_PLAYER_POTENCY[effective_encounter_level]
        )
        if not enemy.is_boss:
            enemy_health *= pow(
                Config.ENEMY_HEALTH_LVL_FALLOFF, (encounter_level - enemy.min_level)
            )
            enemy_health *= roll

        return Encounter(guild_id, enemy.type, encounter_level, enemy_health)

    async def spawn_encounter(
        self,
        guild: discord.Guild,
        enemy_type: EnemyType = None,
        level: int = None,
        owner_id: int = None,
    ):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(
            guild.id, enemy_type=enemy_type, level=level
        )

        context = await self.context_loader.init_encounter_context(encounter)
        context.owner_id = owner_id
        engine = Engine(self.controller, context)
        await engine.run()
        self.engine_cache.append(engine)

        if owner_id is not None:
            event = EncounterEvent(
                datetime.datetime.now(),
                guild.id,
                encounter.id,
                owner_id,
                EncounterEventType.MEMBER_ENGAGE,
            )
            await self.controller.dispatch_event(event)

    async def combatant_turn(
        self,
        context: EncounterContext,
        character: Character,
        skill_data: CharacterSkill,
    ):
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            character.id,
            None,
            skill_data.skill.base_skill.skill_type,
            None,
            None,
            skill_data.skill.id,
            CombatEventType.MEMBER_TURN_ACTION,
        )
        await self.controller.dispatch_event(event)

    async def combatant_timeout(
        self,
        context: EncounterContext,
        character: Character,
    ):
        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            character.id,
            None,
            None,
            None,
            None,
            None,
            CombatEventType.MEMBER_TURN_SKIP,
        )
        await self.controller.dispatch_event(event)

    async def reload_encounter(self, encounter_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)

        for engine in self.engine_cache:
            if engine.context.encounter.id == encounter.id:
                self.engine_cache.remove(engine)
                break

        context = await self.context_loader.load_encounter_context(encounter_id)
        engine = Engine(self.controller, context)

        if context.initiated:
            context._current_actor = context.last_actor
            if context._current_actor is not None:
                context.refresh_initiative()
                context._current_initiative.rotate(-1)
                context._current_actor = context._current_initiative[0]

            if not context.current_actor.is_enemy:
                await self.discord.delete_active_player_input(context.thread)

            engine.current_state = StateType.TURN_END
        elif context.concluded:
            return
        else:
            if context.min_participants > len(context.combatants):
                engine.current_state = StateType.FILLING
            else:
                engine.current_state = StateType.COUNTDOWN

        engine.state = engine.states[engine.current_state]
        self.engine_cache.append(engine)
        await engine.run()
