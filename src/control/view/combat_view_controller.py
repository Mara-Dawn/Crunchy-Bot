import datetime

import discord
from datalayer.database import Database
from discord.ext import commands
from events.encounter_event import EncounterEvent
from events.types import EncounterEventType, UIEventType
from events.ui_event import UIEvent

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

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.COMBAT_ENGAGE:
                interaction = event.payload
                await self.player_engage(interaction)

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
