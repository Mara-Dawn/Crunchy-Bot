import asyncio
import datetime

import discord
from combat.actors import Character
from combat.encounter import Encounter, EncounterContext
from combat.skills.skill import CharacterSkill
from datalayer.database import Database
from discord.ext import commands
from events.bot_event import BotEvent
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, EventType, UIEventType
from events.ui_event import UIEvent

from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.encounter_manager import EncounterManager
from control.combat.object_factory import ObjectFactory
from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


class CombatViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.event_manager: EventManager = controller.get_service(EventManager)
        self.encounter_manager: EncounterManager = controller.get_service(
            EncounterManager
        )
        self.embed_manager: CombatEmbedManager = controller.get_service(
            CombatEmbedManager
        )
        self.factory: ObjectFactory = self.controller.get_service(ObjectFactory)
        self.join_queue = asyncio.Queue()
        self.request_worker = asyncio.create_task(self.join_request_worker())

    async def join_request_worker(self):
        while True:
            interaction = await self.join_queue.get()

            guild_id = interaction.guild_id
            member_id = interaction.user.id

            message = await interaction.original_response()
            encounter = await self.database.get_encounter_by_message_id(
                guild_id, message.id
            )

            encounters = await self.database.get_active_encounter_participants(guild_id)

            already_involved = False
            for _, participants in encounters.items():
                if member_id in participants:
                    await interaction.followup.send(
                        "You are already involved in a currently active encounter.",
                        ephemeral=True,
                    )
                    already_involved = True
                    break

            if already_involved:
                continue

            if encounter.id not in encounters:
                await interaction.followup.send(
                    "This encounter has already concluded.",
                    ephemeral=True,
                )
                continue

            enemy = await self.factory.get_enemy(encounter.enemy_type)
            max_encounter_size = enemy.max_players

            if len(encounters[encounter.id]) >= max_encounter_size:
                await interaction.followup.send(
                    "This encounter is already full.",
                    ephemeral=True,
                )
                continue

            event = EncounterEvent(
                datetime.datetime.now(),
                guild_id,
                encounter.id,
                member_id,
                EncounterEventType.MEMBER_ENGAGE,
            )
            await self.controller.dispatch_event(event)

            self.join_queue.task_done()

    async def listen_for_event(self, event: BotEvent) -> None:
        encounter_id = None
        match event.type:
            case EventType.ENCOUNTER:
                if not event.synchronized:
                    return
                event: EncounterEvent = event
                encounter_id = event.encounter_id

        if encounter_id is not None and event.encounter_event_type in [
            EncounterEventType.MEMBER_ENGAGE,
            EncounterEventType.END,
        ]:
            done = event.encounter_event_type == EncounterEventType.END
            await self.update_encounter_message(encounter_id, done)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_ENGAGE:
                interaction = event.payload
                await self.join_queue.put(interaction)
            case UIEventType.COMBAT_USE_SKILL:
                interaction = event.payload[0]
                skill_data = event.payload[1]
                character = event.payload[2]
                context = event.payload[3]
                await self.player_action(
                    interaction, skill_data, character, context, event.view_id
                )
            case UIEventType.COMBAT_TIMEOUT:
                character = event.payload[0]
                context = event.payload[1]
                await self.player_timeout(character, context)
            case UIEventType.COMBAT_INITIATE:
                encounter = event.payload
                await self.initiate_encounter(encounter)

    async def initiate_encounter(self, encounter: Encounter):
        event = EncounterEvent(
            datetime.datetime.now(),
            encounter.guild_id,
            encounter.id,
            self.bot.user.id,
            EncounterEventType.INITIATE,
        )
        await self.controller.dispatch_event(event)

    async def update_encounter_message(self, encounter_id: int, done: bool):
        encounter = await self.database.get_encounter_by_encounter_id(encounter_id)
        embed = await self.embed_manager.get_spawn_embed(encounter, done=done)
        event = UIEvent(UIEventType.COMBAT_ENGAGE_UPDATE, (encounter_id, embed, done))
        await self.controller.dispatch_ui_event(event)

    async def player_action(
        self,
        interaction: discord.Interaction,
        skill_data: CharacterSkill,
        character: Character,
        context: EncounterContext,
        view_id: int,
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        message = await interaction.original_response()
        await message.delete()

        current_context = await self.encounter_manager.load_encounter_context(
            context.encounter.id
        )

        await self.encounter_manager.combatant_turn(
            current_context, character, skill_data
        )

        self.controller.detach_view_by_id(view_id)

    async def player_timeout(
        self,
        character: Character,
        context: EncounterContext,
    ):
        current_context = await self.encounter_manager.load_encounter_context(
            context.encounter.id
        )

        await self.encounter_manager.combatant_timeout(current_context, character)
