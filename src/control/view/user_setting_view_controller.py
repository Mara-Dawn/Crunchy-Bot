from typing import Any

import discord
from discord.ext import commands

from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.types import UserSettingType
from control.user_settings_manager import UserSettingsManager
from control.view.view_controller import ViewController
from datalayer.database import Database
from events.types import UIEventType
from events.ui_event import UIEvent
from view.settings.view import (
    EditUserSettingModal,
    UserSettingsViewState,
)


class UserSettingViewController(ViewController):

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
        self.user_settings_manager: UserSettingsManager = self.controller.get_service(
            UserSettingsManager
        )

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.USER_SETTING_EDIT:
                interaction = event.payload[0]
                setting_type = event.payload[1]
                await self.edit_setting(interaction, setting_type, event.view_id)
            case UIEventType.USER_SETTING_APPLY:
                interaction = event.payload[0]
                setting_type = event.payload[1]
                value = event.payload[2]
                await self.apply_setting(
                    interaction, setting_type, value, event.view_id
                )

    async def apply_setting(
        self,
        interaction: discord.Interaction,
        setting_type: UserSettingType | None,
        value: Any,
        view_id: int,
    ):
        if setting_type is None:
            await interaction.followup.send(
                "Please select a setting first.",
                ephemeral=True,
            )
            return

        setting_definition = self.user_settings_manager.get_definition(setting_type)
        try:
            value = setting_definition.value_type(value)
        except ValueError:
            await interaction.followup.send(
                "Invalid Value.",
                ephemeral=True,
            )
            return

        await self.user_settings_manager.set(
            interaction.user.id, interaction.guild_id, setting_type, value
        )

        event = UIEvent(
            UIEventType.USER_SETTING_REFRESH,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)

    async def edit_setting(
        self,
        interaction: discord.Interaction,
        setting_type: UserSettingType | None,
        view_id: int,
    ):
        if setting_type is None:
            await interaction.response.send_message(
                "Please select a setting first.",
                ephemeral=True,
            )
            return

        setting_definition = self.user_settings_manager.get_definition(setting_type)
        current = await self.user_settings_manager.get(
            interaction.user.id, interaction.guild_id, setting_type
        )

        if setting_definition.options is None:
            view = self.controller.get_view(view_id)
            modal = EditUserSettingModal(view, setting_definition, current)
            await interaction.response.send_modal(modal)
            return

        await interaction.response.defer()

        event = UIEvent(
            UIEventType.USER_SETTING_REFRESH,
            None,
            view_id,
        )
        await self.controller.dispatch_ui_event(event)
