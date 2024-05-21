import asyncio
import datetime
import random

import discord
from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext
from combat.enemies import *  # noqa: F403
from combat.enemies.types import EnemyType
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_enemy_manager import CombatEnemyManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import CombatEventType, EncounterEventType, EventType
from view.combat.combat_turn_view import CombatTurnView
from view.combat.engage_view import EnemyEngageView


class EncounterManager(Service):

    TURN_WAIT = 4

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
        self.enemy_manager: CombatEnemyManager = self.controller.get_service(
            CombatEnemyManager
        )
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.log_name = "Encounter"

    async def listen_for_event(self, event: BotEvent):
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                match encounter_event.encounter_event_type:
                    case EncounterEventType.MEMBER_ENGAGE:
                        await self.add_member_to_encounter(
                            encounter_event.encounter_id, encounter_event.member_id
                        )
                    case (
                        EncounterEventType.ENEMY_DEFEAT
                        | EncounterEventType.MEMBER_DEFEAT
                    ):
                        if not event.synchronized:
                            return
                        await self.refresh_encounter_thread(
                            encounter_event.encounter_id
                        )

            case EventType.COMBAT:
                combat_event: CombatEvent = event
                if not event.synchronized:
                    return
                await self.refresh_encounter_thread(combat_event.encounter_id)

    async def create_encounter(self, guild_id: int):
        encounter_level = await self.database.get_guild_level(guild_id)

        enemies = [self.enemy_manager.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy for enemy in enemies if enemy.level <= encounter_level
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        enemy_health = random.randint(enemy.min_hp, enemy.max_hp)

        return Encounter(guild_id, enemy.type, enemy_health)

    async def spawn_encounter(self, guild: discord.Guild, channel_id: int):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(guild.id)
        embed = self.embed_manager.get_spawn_embed(encounter)

        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)

        view = EnemyEngageView(self.controller)
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        channel = guild.get_channel(channel_id)

        message = await channel.send("", embed=embed, view=view, files=[image])
        encounter.message_id = message.id
        encounter.channel_id = message.channel.id

        encounter_id = await self.database.log_encounter(encounter)

        event = EncounterEvent(
            datetime.datetime.now(),
            guild.id,
            encounter_id,
            self.bot.user.id,
            EncounterEventType.SPAWN,
        )
        await self.controller.dispatch_event(event)

    async def create_encounter_thread(self, encounter: Encounter) -> discord.Thread:
        channel = self.bot.get_channel(encounter.channel_id)
        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)
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
        new_thread = False

        if thread_id is None:
            thread = await self.create_encounter_thread(encounter)
            new_thread = True
        else:
            thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        if thread is None:
            return

        user = self.bot.get_guild(encounter.guild_id).get_member(member_id)
        await thread.add_user(user)

        embed = self.embed_manager.get_actor_join_embed(user)
        await thread.send("", embed=embed)

        if new_thread:
            await self.refresh_encounter_thread(encounter_id)

    async def load_encounter_context(self, encounter_id) -> EncounterContext:
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)
        opponent = self.actor_manager.get_opponent(
            enemy, encounter.max_hp, encounter_events, combat_events
        )

        combatant_ids = await self.database.get_encounter_participants_by_encounter_id(
            encounter_id
        )
        guild = self.bot.get_guild(encounter.guild_id)
        members = [guild.get_member(id) for id in combatant_ids]

        combatants = []

        for member in members:
            combatant = self.actor_manager.get_character(
                member, encounter_events, combat_events
            )
            combatants.append(combatant)

        return EncounterContext(
            encounter=encounter,
            opponent=opponent,
            encounter_events=encounter_events,
            combat_events=combat_events,
            combatants=combatants,
            thread=thread,
        )

    async def skip_turn(self, actor: Actor, context: EncounterContext):

        embed = self.embed_manager.get_turn_skip_embed(
            actor, f"{actor.name} is defeated.", context
        )
        await context.thread.send("", embed=embed)

        combat_event_type = CombatEventType.MEMBER_SKIP_TURN
        if actor.is_enemy:
            combat_event_type = CombatEventType.ENEMY_SKIP_TURN

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            actor.id,
            actor.id,
            None,
            None,
            combat_event_type,
        )
        await self.controller.dispatch_event(event)

    async def opponent_turn(self, context: EncounterContext):
        opponent = context.opponent

        skill = random.choice(opponent.skills)
        skill_data = opponent.get_skill_data(skill)
        damage_instance = opponent.get_skill_damage(skill)

        target = random.choice(context.combatants)

        await self.embed_manager.handle_actor_turn_embed(
            opponent, target, skill_data, damage_instance, context
        )
        await asyncio.sleep(2)

        event = CombatEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            opponent.id,
            target.id,
            skill.type,
            damage_instance.value,
            CombatEventType.ENEMY_TURN,
        )
        await self.controller.dispatch_event(event)

    async def conclude_encounter(self, context: EncounterContext, success: bool = True):

        if success:
            embed = self.embed_manager.get_combat_success_embed(context)
        else:
            embed = self.embed_manager.get_combat_failed_embed(context)

        enemy = context.opponent.enemy
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        await context.thread.send("", embed=embed, files=[image])

        event = EncounterEvent(
            datetime.datetime.now(),
            context.encounter.guild_id,
            context.encounter.id,
            self.bot.user.id,
            EncounterEventType.END,
        )
        await self.controller.dispatch_event(event)

    async def context_needs_update_check(self, context: EncounterContext) -> bool:
        already_defeated = []
        update_context = False

        for event in context.encounter_events:
            match event.encounter_event_type:
                case EncounterEventType.MEMBER_DEFEAT | EncounterEventType.ENEMY_DEFEAT:
                    already_defeated.append(event.member_id)

        for actor in context.actors:
            health = self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )

            if health <= 0 and actor.id not in already_defeated:
                encounter_event_type = EncounterEventType.MEMBER_DEFEAT
                if actor.is_enemy:
                    encounter_event_type = EncounterEventType.ENEMY_DEFEAT

                embed = self.embed_manager.get_actor_defeated_embed(actor)
                await context.thread.send("", embed=embed)

                event = EncounterEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    actor.id,
                    encounter_event_type,
                )
                await self.controller.dispatch_event(event)

                update_context = True

        return update_context

    async def delete_previous_combat_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None:
                    await message.delete()
                    break

    async def get_previous_combat_info(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) == 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.image.url is not None:
                    return message
        return None

    async def refresh_encounter_thread(self, encounter_id: int):
        context = await self.load_encounter_context(encounter_id)

        if await self.context_needs_update_check(context):
            return

        if context.is_concluded():
            return

        if context.opponent.defeated:
            await self.delete_previous_combat_info(context.thread)
            await self.conclude_encounter(context)
            return

        if len(self.actor_manager.get_undefeated_actors(context.combatants)) <= 0:
            await self.delete_previous_combat_info(context.thread)
            await self.conclude_encounter(context, success=False)
            return

        current_actor = context.get_current_actor()

        embed = self.embed_manager.get_combat_embed(context)

        if current_actor.id == context.beginning_actor.id:
            notification = self.embed_manager.get_notification_embed("New Round")
            await context.thread.send(content="", embed=notification)

            await self.delete_previous_combat_info(context.thread)
            enemy = context.opponent.enemy
            image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
            await context.thread.send("", embed=embed, files=[image])
        else:
            message = await self.get_previous_combat_info(context.thread)
            if message is not None:
                await message.edit(embed=embed)

        await asyncio.sleep(2)

        if current_actor.is_enemy:
            await self.opponent_turn(context)
            return

        if current_actor.defeated:
            await self.skip_turn(current_actor, context)
            return

        embed = self.embed_manager.get_character_turn_embed(context)
        view = CombatTurnView(self.controller, current_actor, context)
        await context.thread.send(f"<@{current_actor.id}>", embed=embed, view=view)
        return
