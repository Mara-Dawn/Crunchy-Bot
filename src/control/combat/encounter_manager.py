import asyncio
import datetime
import random

import discord
from combat.actors import Actor, Character
from combat.encounter import Encounter, EncounterContext, TurnData
from combat.enemies import *  # noqa: F403
from combat.enemies.types import EnemyType
from combat.skills.skill import CharacterSkill
from combat.skills.types import SkillEffect
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.combat_enemy_manager import CombatEnemyManager
from control.combat.combat_gear_manager import CombatGearManager
from control.combat.combat_skill_manager import CombatSkillManager
from control.controller import Controller
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord.ext import commands
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType, CombatEventType, EncounterEventType, EventType
from view.combat.combat_turn_view import CombatTurnView
from view.combat.engage_view import EnemyEngageView


class EncounterManager(Service):

    TURN_WAIT = 4
    ENCOUNTER_MIN_LVL_SCALING = 0.65

    # based on avg player strength
    ENEMY_HEALTH_SCALING = {
        1: 11,
        2: 34,
        3: 72,
        4: 142,
        5: 204,
        6: 341,
        7: 461,
        8: 589,
        9: 764,
        10: 1114,
        11: 1486,
        12: 1751,
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
        self.enemy_manager: CombatEnemyManager = self.controller.get_service(
            CombatEnemyManager
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
                if combat_event.combat_event_type not in [
                    CombatEventType.ENEMY_END_TURN,
                    CombatEventType.MEMBER_END_TURN,
                ]:
                    return
                await self.refresh_encounter_thread(combat_event.encounter_id)

    async def create_encounter(self, guild_id: int):
        max_encounter_level = await self.database.get_guild_level(guild_id)
        min_encounter_level = max(
            1, int(max_encounter_level * self.ENCOUNTER_MIN_LVL_SCALING)
        )

        encounter_level = random.randint(min_encounter_level, max_encounter_level)

        enemies = [self.enemy_manager.get_enemy(enemy_type) for enemy_type in EnemyType]
        possible_enemies = [
            enemy
            for enemy in enemies
            if encounter_level >= enemy.min_level and encounter_level <= enemy.max_level
        ]

        spawn_weights = [enemy.weighting for enemy in possible_enemies]
        spawn_weights = [1.0 / w for w in spawn_weights]
        sum_weights = sum(spawn_weights)
        spawn_weights = [w / sum_weights for w in spawn_weights]

        enemy = random.choices(possible_enemies, weights=spawn_weights)[0]
        roll = random.uniform(0.95, 1.05)
        enemy_health = enemy.health * self.ENEMY_HEALTH_SCALING[encounter_level]
        enemy_health *= roll

        return Encounter(guild_id, enemy.type, encounter_level, enemy_health)

    async def spawn_encounter(self, guild: discord.Guild, channel_id: int):
        log_message = f"Encounter was spawned in {guild.name}."
        self.logger.log(guild.id, log_message, cog=self.log_name)

        encounter = await self.create_encounter(guild.id)
        embed = await self.embed_manager.get_spawn_embed(encounter)

        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)

        view = EnemyEngageView(self.controller)
        image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
        channel = guild.get_channel(channel_id)

        message = await channel.send("", embed=embed, view=view, files=[image])
        encounter.message_id = message.id
        encounter.channel_id = message.channel.id

        encounter_id = await self.database.log_encounter(encounter)

        view.set_message(message)
        await view.refresh_ui(embed=embed, encounter_id=encounter_id)

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

    async def apply_late_join_penalty(self, encounter_id: int, member_id: int) -> str:
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        enemy = self.enemy_manager.get_enemy(encounter.enemy_type)
        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter.enemy_level,
            encounter.max_hp,
            encounter_events,
            combat_events,
        )

        max_enemy_hp = encounter.max_hp
        current_enemy_hp = await self.actor_manager.get_actor_current_hp(
            opponent, combat_events
        )

        combat_progress = current_enemy_hp / max_enemy_hp

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

    async def add_member_to_encounter(self, encounter_id: int, member_id: int):
        thread_id = await self.database.get_encounter_thread(encounter_id)

        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        thread = None
        new_thread = False
        additional_message = ""

        if thread_id is None:
            thread = await self.create_encounter_thread(encounter)
            new_thread = True
        else:
            thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

            additional_message = await self.apply_late_join_penalty(
                encounter_id, member_id
            )

        if thread is None:
            return

        user = self.bot.get_guild(encounter.guild_id).get_member(member_id)
        await thread.add_user(user)

        embed = self.embed_manager.get_actor_join_embed(
            user, additional_message=additional_message
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        turn_message = await self.get_previous_turn_message(thread)
        if turn_message is None:
            await thread.send("", embed=embed)
        else:
            previous_embeds = turn_message.embeds
            embeds = previous_embeds + [embed]
            await turn_message.edit(embeds=embeds)

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
        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter.enemy_level,
            encounter.max_hp,
            encounter_events,
            combat_events,
        )

        combatant_ids = await self.database.get_encounter_participants_by_encounter_id(
            encounter_id
        )
        guild = self.bot.get_guild(encounter.guild_id)
        members = [guild.get_member(id) for id in combatant_ids]

        combatants = []

        for member in members:
            combatant = await self.actor_manager.get_character(
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

    async def skip_turn(
        self,
        actor: Actor,
        context: EncounterContext,
    ):

        turn_message = await self.get_previous_turn_message(context.thread)
        embed = self.embed_manager.get_turn_skip_embed(
            actor, f"{actor.name} is defeated.", context
        )
        previous_embeds = turn_message.embeds
        current_embeds = previous_embeds + [embed]
        await turn_message.edit(embeds=current_embeds)

        combat_event_type = CombatEventType.MEMBER_END_TURN
        if actor.is_enemy:
            combat_event_type = CombatEventType.ENEMY_END_TURN

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

        return embed

    async def opponent_turn(self, context: EncounterContext):
        opponent = context.opponent

        turn_data = await self.actor_manager.calculate_opponent_turn(context)

        turn_message = await self.get_previous_turn_message(context.thread)
        previous_embeds = turn_message.embeds

        image = discord.File(
            f"./img/enemies/{opponent.enemy.image}", opponent.enemy.image
        )

        initial_embed = True
        async for embed in self.embed_manager.handle_actor_turn_embed(
            turn_data, context
        ):
            attachments = [image]
            current_embeds = previous_embeds + [embed]

            if initial_embed:
                initial_embed = False
                await turn_message.edit(embeds=current_embeds, attachments=attachments)
            else:
                await turn_message.edit(embeds=current_embeds)

        await asyncio.sleep(2)

        for turn in turn_data:
            for target, damage_instance, _ in turn.damage_data:
                total_damage = target.get_damage_after_defense(
                    turn.skill, damage_instance.scaled_value
                )
                event = CombatEvent(
                    datetime.datetime.now(),
                    context.encounter.guild_id,
                    context.encounter.id,
                    opponent.id,
                    target.id,
                    turn.skill.base_skill.skill_type,
                    total_damage,
                    None,
                    CombatEventType.ENEMY_TURN,
                )
                await self.controller.dispatch_event(event)

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

    async def combatant_turn(
        self,
        context: EncounterContext,
        character: Character,
        skill_data: CharacterSkill,
        target: Actor = None,
    ):
        if target is None:
            target = await self.skill_manager.get_character_default_target(
                character, skill_data.skill, context
            )

        skill_instances = character.get_skill_effect(
            skill_data.skill, combatant_count=len(context.combatants)
        )

        turn_message = await self.get_previous_turn_message(context.thread)
        previous_embeds = turn_message.embeds

        skill_value_data = []
        hp_cache = {}

        for instance in skill_instances:
            total_skill_value = target.get_damage_after_defense(
                skill_data.skill, instance.scaled_value
            )

            target_id = target.id
            if target_id is None:
                target_id = -1

            if target_id not in hp_cache:
                hp_cache[target_id] = await self.actor_manager.get_actor_current_hp(
                    target, context.combat_events
                )

            current_hp = hp_cache[target_id]

            if skill_data.skill.base_skill.skill_effect != SkillEffect.HEALING:
                total_skill_value *= -1

            new_target_hp = min(
                max(0, current_hp + total_skill_value), character.max_hp
            )
            skill_value_data.append((target, instance, new_target_hp))

        turn_data = [TurnData(character, skill_data.skill, skill_value_data)]

        async for embed in self.embed_manager.handle_actor_turn_embed(
            turn_data, context
        ):
            current_embeds = previous_embeds + [embed]
            await turn_message.edit(embeds=current_embeds, attachments=[])

        await asyncio.sleep(2)

        for turn in turn_data:
            for target, damage_instance, _ in turn.damage_data:
                total_damage = target.get_damage_after_defense(
                    turn.skill, damage_instance.scaled_value
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

    async def conclude_encounter(self, context: EncounterContext, success: bool = True):

        if success:
            embed = await self.embed_manager.get_combat_success_embed(context)
        else:
            embed = await self.embed_manager.get_combat_failed_embed(context)

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

        if success:
            await self.payout_loot(context)

    async def payout_loot(self, context: EncounterContext):
        loot = await self.gear_manager.roll_enemy_loot(context)

        now = datetime.datetime.now()

        for member, member_loot in loot.items():

            await asyncio.sleep(2)
            beans = member_loot[0]
            embeds = []
            loot_head_embed = await self.embed_manager.get_loot_embed(member, beans)
            embeds.append(loot_head_embed)

            message = await context.thread.send(f"<@{member.id}>", embeds=embeds)

            event = BeansEvent(
                now,
                member.guild.id,
                BeansEventType.COMBAT_LOOT,
                member.id,
                beans,
            )
            await self.controller.dispatch_event(event)

            already_dropped = []
            for drop in member_loot[1]:
                embeds.append(drop.get_embed())

                await asyncio.sleep(2.5)

                already_dropped.append(drop)

                files = {}
                for drop in already_dropped:

                    file_path = f"./{drop.base.image_path}{drop.base.image}"
                    if file_path not in files:
                        file = discord.File(
                            file_path,
                            drop.base.attachment_name,
                        )
                        files[file_path] = file

                attachments = list(files.values())
                await message.edit(embeds=embeds, attachments=attachments)

            # files = list(files.values())
            item = member_loot[2]
            if item is not None:
                embeds.append(item.get_embed(self.bot, show_price=False))

                await asyncio.sleep(2.5)

                await message.edit(embeds=embeds)

                event = InventoryEvent(
                    now,
                    member.guild.id,
                    member.id,
                    item.type,
                    1,
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
            health = await self.actor_manager.get_actor_current_hp(
                actor, context.combat_events
            )

            if health <= 0 and actor.id not in already_defeated:
                encounter_event_type = EncounterEventType.MEMBER_DEFEAT
                if actor.is_enemy:
                    encounter_event_type = EncounterEventType.ENEMY_DEFEAT

                embed = self.embed_manager.get_actor_defeated_embed(actor)

                turn_message = await self.get_previous_turn_message(context.thread)
                if turn_message is None:
                    await context.thread.send("", embed=embed)
                else:
                    previous_embeds = turn_message.embeds
                    embeds = previous_embeds + [embed]
                    await turn_message.edit(embeds=embeds)

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

    async def get_previous_turn_message(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) >= 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.title == "New Round":
                    return message
        return None

    async def get_previous_enemy_info(self, thread: discord.Thread):
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

        enemy_embed = await self.embed_manager.get_combat_embed(context)
        round_embed = await self.embed_manager.get_round_embed(context)

        if current_actor.id == context.beginning_actor.id:

            await self.delete_previous_combat_info(context.thread)
            enemy = context.opponent.enemy
            image = discord.File(f"./img/enemies/{enemy.image}", enemy.image)
            await context.thread.send("", embed=enemy_embed, files=[image])

            await context.thread.send(content="", embed=round_embed)

        else:
            message = await self.get_previous_enemy_info(context.thread)
            if message is not None:
                await message.edit(embed=enemy_embed)
            round_message = await self.get_previous_turn_message(context.thread)
            if round_message is not None:
                round_embeds = round_message.embeds
                round_embeds[0] = round_embed
                await round_message.edit(embeds=round_embeds)

        await asyncio.sleep(2)

        if current_actor.is_enemy:
            await self.opponent_turn(context)
            return

        if current_actor.defeated:
            await self.skip_turn(current_actor, context)
            return

        enemy_embeds, files = await self.embed_manager.get_character_turn_embeds(
            context
        )
        view = CombatTurnView(self.controller, current_actor, context)
        await context.thread.send(
            f"<@{current_actor.id}>", embeds=enemy_embeds, files=files, view=view
        )
        return
