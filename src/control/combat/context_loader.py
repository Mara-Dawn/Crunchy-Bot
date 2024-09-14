import asyncio
from collections.abc import AsyncGenerator

import discord
from discord.ext import commands

from combat.actors import Actor
from combat.encounter import Encounter, EncounterContext
from control.combat.combat_actor_manager import CombatActorManager
from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.object_factory import ObjectFactory
from control.combat.status_effect_manager import CombatStatusEffectManager
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from datalayer.database import Database
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.status_effect_event import StatusEffectEvent
from events.types import EncounterEventType, EventType


class ContextLoader(Service):

    RETRY_LIMIT = 5

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.actor_manager: CombatActorManager = self.controller.get_service(
            CombatActorManager
        )
        self.embed_manager: CombatEmbedManager = self.controller.get_service(
            CombatEmbedManager
        )
        self.status_effect_manager: CombatStatusEffectManager = (
            self.controller.get_service(CombatStatusEffectManager)
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.log_name = "ContextLoader"

        self.context_cache: dict[int, EncounterContext] = {}

    async def listen_for_event(self, event: BotEvent):
        if not event.synchronized:
            return
        match event.type:
            case EventType.ENCOUNTER:
                encounter_event: EncounterEvent = event
                encounter_id = encounter_event.encounter_id

                if encounter_id in self.context_cache:
                    context = self.context_cache[encounter_id]
                    context.apply_event(event)
                    for actor in context.actors:
                        await self.actor_manager.apply_event(actor, event)

                    match encounter_event.encounter_event_type:
                        case EncounterEventType.NEW_ROUND:
                            for actor in context.initiative:
                                actor.round_modifier = await self.status_effect_manager.handle_attribute_status_effects(
                                    context, actor
                                )

                            context.refresh_initiative()
                        case EncounterEventType.MEMBER_ENGAGE:
                            await self.add_character_to_encounter(
                                encounter_id, encounter_event.member_id
                            )
                        case EncounterEventType.END:
                            del self.context_cache[encounter_id]
                            return

            case EventType.COMBAT:
                event: CombatEvent = event
                encounter_id = event.encounter_id
                if encounter_id in self.context_cache:
                    context = self.context_cache[encounter_id]
                    context.apply_event(event)
                    for actor in context.actors:
                        await self.actor_manager.apply_event(actor, event)

            case EventType.STATUS_EFFECT:
                event: StatusEffectEvent = event
                encounter_id = event.encounter_id
                if encounter_id in self.context_cache:
                    context = self.context_cache[encounter_id]
                    context.apply_event(event)
                    for actor in context.actors:
                        await self.actor_manager.apply_event(actor, event)

    async def add_character_to_encounter(self, encounter_id: int, member_id: int):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        guild = self.bot.get_guild(encounter.guild_id)
        member = guild.get_member(member_id)
        context = self.context_cache[encounter_id]

        combatant = await self.actor_manager.get_character(
            member,
            context.encounter_events,
            context.combat_events,
            context.status_effects,
        )

        self.context_cache[encounter_id].add_combatant(combatant)

    async def load_encounter_context(self, encounter_id) -> EncounterContext:
        if encounter_id in self.context_cache:
            return self.context_cache[encounter_id]

        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        encounter_events = await self.database.get_encounter_events_by_encounter_id(
            encounter_id
        )
        combat_events = await self.database.get_combat_events_by_encounter_id(
            encounter_id
        )
        status_effects = await self.database.get_status_effects_by_encounter(
            encounter_id
        )
        thread_id = await self.database.get_encounter_thread(encounter_id)
        thread = self.bot.get_channel(encounter.channel_id).get_thread(thread_id)

        enemy = await self.factory.get_enemy(encounter.enemy_type)

        opponent = await self.actor_manager.get_opponent(
            enemy,
            encounter,
            encounter_events,
            combat_events,
            status_effects,
        )

        combatant_ids = await self.database.get_encounter_participants_by_encounter_id(
            encounter_id
        )

        guild = self.bot.get_guild(encounter.guild_id)
        members = [guild.get_member(id) for id in combatant_ids]

        combatants = []

        for member in members:

            combatant = await self.actor_manager.get_character(
                member, encounter_events, combat_events, status_effects
            )

            combatants.append(combatant)

        context = EncounterContext(
            encounter=encounter,
            opponent=opponent,
            encounter_events=encounter_events,
            combat_events=combat_events,
            status_effects=status_effects,
            combatants=combatants,
            thread=thread,
        )

        outcome = await self.status_effect_manager.handle_attribute_status_effects(
            context, context.opponent
        )
        context.opponent.round_modifier = outcome

        for combatant in context.combatants:
            outcome = await self.status_effect_manager.handle_attribute_status_effects(
                context, combatant
            )
            combatant.round_modifier = outcome

        self.context_cache[encounter_id] = context
        return self.context_cache[encounter_id]

    async def get_previous_turn_message(self, thread: discord.Thread):
        async for message in thread.history(limit=100):
            if len(message.embeds) >= 1 and message.author.id == self.bot.user.id:
                embed = message.embeds[0]
                if embed.title == "New Round" or embed.title == "Round Continued..":
                    return message
        return None

    async def append_embed_generator_to_round(
        self, context: EncounterContext, generator: AsyncGenerator
    ):
        thread = context.thread
        message = await self.get_previous_turn_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds

        async for embed in generator:
            current_embeds = previous_embeds + [embed]
            await self.edit_message(message, embeds=current_embeds)

    async def append_embed_to_round(
        self, context: EncounterContext, embed: discord.Embed
    ):
        thread = context.thread
        message = await self.get_previous_turn_message(thread)

        if len(message.embeds) >= 10:
            round_embed = await self.embed_manager.get_round_embed(context, cont=True)
            message = await self.send_message(
                context.thread, content="", embed=round_embed
            )

        previous_embeds = message.embeds
        current_embeds = previous_embeds + [embed]
        await self.edit_message(message, embeds=current_embeds)

    async def append_embeds_to_round(
        self, context: EncounterContext, actor: Actor, embed_data: dict[str, str]
    ):
        message = None
        if len(embed_data) <= 0:
            return message
        status_effect_embed = self.embed_manager.get_status_effect_embed(
            actor, embed_data
        )
        message = await self.append_embed_to_round(context, status_effect_embed)
        return message

    async def edit_message(self, message: discord.Message, **kwargs):
        retries = 0
        success = False
        new_message = None
        while not success and retries <= self.RETRY_LIMIT:
            try:
                new_message = await message.edit(**kwargs)
                success = True
            except (discord.HTTPException, discord.DiscordServerError) as e:
                self.logger.log(message.guild.id, e.text, self.log_name)
                retries += 1
                await asyncio.sleep(5)

        if not success:
            self.logger.error(message.guild.id, "edit message timeout", self.log_name)

        return new_message

    async def send_message(self, channel: discord.channel.TextChannel, **kwargs):
        retries = 0
        success = False
        message = None
        while not success and retries <= self.RETRY_LIMIT:
            try:
                message = await channel.send(**kwargs)
                success = True
            except (discord.HTTPException, discord.DiscordServerError) as e:
                self.logger.log(channel.guild.id, e.text, self.log_name)
                retries += 1
                await asyncio.sleep(5)

        if not success:
            self.logger.error(message.guild.id, "send message timeout", self.log_name)

        return message
