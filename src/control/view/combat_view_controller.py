import asyncio
import datetime

import discord
from combat.actors import Character
from combat.encounter import EncounterContext
from combat.skills.skill import SkillData
from datalayer.database import Database
from discord.ext import commands
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.types import CombatEventType, EncounterEventType, UIEventType
from events.ui_event import UIEvent

from control.combat.combat_embed_manager import CombatEmbedManager
from control.combat.encounter_manager import EncounterManager
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

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_ENGAGE:
                interaction = event.payload
                await self.player_engage(interaction)
            case UIEventType.COMBAT_USE_SKILL:
                interaction = event.payload[0]
                skill_data = event.payload[1]
                character = event.payload[2]
                context = event.payload[3]
                await self.player_action(
                    interaction, skill_data, character, context, event.view_id
                )

    async def player_engage(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        member_id = interaction.user.id

        message = await interaction.original_response()
        encounter = await self.database.get_encounter_by_message_id(
            guild_id, message.id
        )

        encounters = await self.database.get_active_encounter_participants(guild_id)

        for _, participants in encounters.items():
            if member_id in participants:
                await interaction.followup.send(
                    "You are already involved in a currently active encounter.",
                    ephemeral=True,
                )
                return

        if encounter.id not in encounters:
            await interaction.followup.send(
                "This encounter has already concluded.",
                ephemeral=True,
            )
            return

        event = EncounterEvent(
            datetime.datetime.now(),
            guild_id,
            encounter.id,
            member_id,
            EncounterEventType.MEMBER_ENGAGE,
        )
        await self.controller.dispatch_event(event)

    async def player_action(
        self,
        interaction: discord.Interaction,
        skill_data: SkillData,
        character: Character,
        context: EncounterContext,
        view_id: int,
    ):
        event = UIEvent(UIEventType.STOP_INTERACTIONS, None, view_id)
        await self.controller.dispatch_ui_event(event)

        guild_id = interaction.guild_id
        member_id = interaction.user.id

        skill_value = character.get_skill_value(skill_data)

        message = await interaction.original_response()

        await self.embed_manager.handle_actor_turn_embed(
            character,
            context.opponent,
            skill_data,
            skill_value,
            context,
            message=message,
        )
        await asyncio.sleep(2)

        self.controller.detach_view_by_id(view_id)

        event = CombatEvent(
            datetime.datetime.now(),
            guild_id,
            context.encounter.id,
            member_id,
            context.opponent.id,
            skill_data.skill.type,
            skill_value,
            CombatEventType.MEMBER_TURN,
        )
        await self.controller.dispatch_event(event)
