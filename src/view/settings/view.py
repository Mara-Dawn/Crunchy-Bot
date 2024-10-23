import contextlib
from enum import Enum
from typing import Any

import discord

from control.controller import Controller
from control.types import ControllerType, UserSettingType
from control.user_settings_manager import UserSettingsManager
from datalayer.settings import UserSetting
from events.types import UIEventType
from events.ui_event import UIEvent
from view.settings.embed import UserSettingsEmbed
from view.view_menu import ViewMenu


class UserSettingsViewState(Enum):
    DROPDOWN = 0
    EDIT = 1


class UserSettingView(ViewMenu):

    def __init__(
        self,
        controller: Controller,
        interaction: discord.Interaction,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_name = interaction.guild.name
        self.member_id = interaction.user.id
        self.member = interaction.user
        self.guild_id = interaction.guild_id

        self.selected = None
        self.selected_definition = None
        self.selected_option = None

        self.state = UserSettingsViewState.EDIT

        self.message = None

        self.user_settings_manager: UserSettingsManager = self.controller.get_service(
            UserSettingsManager
        )

        self.definitions: list[UserSetting] = [
            self.user_settings_manager.get_definition(setting_type)
            for setting_type in UserSettingType
        ]

        self.controller_types = [ControllerType.USER_SETTING]
        self.controller.register_view(self)
        self.refresh_elements()

    async def listen_for_ui_event(self, event: UIEvent):
        if event.view_id != self.id:
            return
        match event.type:
            case UIEventType.USER_SETTING_REFRESH:
                await self.refresh_ui()

    async def apply_setting(
        self, interaction: discord.Interaction, setting: UserSettingType, value: Any
    ):
        await interaction.response.defer()
        event = UIEvent(
            UIEventType.USER_SETTING_APPLY,
            (interaction, setting, value),
            self.id,
        )
        self.selected_option = None
        await self.controller.dispatch_ui_event(event)

    async def apply_button(self, interaction: discord.Interaction):
        await self.apply_setting(interaction, self.selected, self.selected_option)

    async def edit(
        self,
        interaction: discord.Interaction,
    ):
        event = UIEvent(
            UIEventType.USER_SETTING_EDIT,
            (interaction, self.selected),
            self.id,
        )
        await self.controller.dispatch_ui_event(event)

    def refresh_elements(self, disabled: bool = False):
        self.clear_items()
        self.add_item(
            SettingsDropdown(self.definitions, self.selected, disabled=disabled)
        )

        match self.state:
            case UserSettingsViewState.EDIT:
                self.add_item(EditButton(disabled=disabled))
            case UserSettingsViewState.DROPDOWN:
                self.add_item(
                    EditSettingDropdown(
                        self.selected,
                        self.selected_definition.options,
                        self.selected_option,
                        disabled=disabled,
                    )
                )
                self.add_item(ApplyButton(disabled=disabled))

    async def refresh_ui(
        self,
        disabled: bool = False,
    ):
        if self.message is None:
            return

        if self.selected is None:
            self.selected = UserSettingType.GAMBA_DEFAULT

        self.selected_definition = self.user_settings_manager.get_definition(
            self.selected
        )
        if self.selected_option is None:
            self.selected_option = await self.user_settings_manager.get(
                self.member_id, self.guild_id, self.selected
            )

        self.refresh_elements(disabled)

        embed = UserSettingsEmbed(self.member, self.user_settings_manager)
        await embed.load_settings()
        await self.message.edit(embed=embed, view=self)

    async def set_selected(
        self, interaction: discord.Interaction, selected_setting: UserSettingType | None
    ):
        await interaction.response.defer()
        self.selected = selected_setting
        self.selected_option = None

        setting_definition = self.user_settings_manager.get_definition(self.selected)
        if setting_definition.options is None:
            self.state = UserSettingsViewState.EDIT
        else:
            self.state = UserSettingsViewState.DROPDOWN

        await self.refresh_ui()

    async def set_selected_option(
        self, interaction: discord.Interaction, option: Any | None
    ):
        await interaction.response.defer()
        self.selected_option = option
        await self.refresh_ui()

    async def on_timeout(self):
        with contextlib.suppress(discord.HTTPException):
            await self.message.edit(view=None)
        self.controller.detach_view(self)


class EditButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):

        super().__init__(
            label="Edit",
            style=discord.ButtonStyle.green,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: UserSettingView = self.view

        if await view.interaction_check(interaction):
            await view.edit(interaction)


class ApplyButton(discord.ui.Button):

    def __init__(self, disabled: bool = True):

        super().__init__(
            label="Apply",
            style=discord.ButtonStyle.green,
            row=2,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: UserSettingView = self.view

        if await view.interaction_check(interaction):
            await self.view.apply_button(interaction)


class EditUserSettingModal(discord.ui.Modal):

    def __init__(
        self,
        view: UserSettingView,
        setting: UserSetting,
        current: str | None,
    ):
        super().__init__(title=setting.title)

        self.view = view
        self.setting = setting.setting_type

        self.value_input = discord.ui.TextInput(
            label=setting.description,
            placeholder=setting.description,
        )

        if current is not None:
            self.value_input.default = current

        self.add_item(self.value_input)

    async def on_submit(self, interaction: discord.Interaction):
        await self.view.apply_setting(interaction, self.setting, self.value_input.value)


class EditSettingDropdown(discord.ui.Select):

    def __init__(
        self,
        setting: UserSettingType,
        setting_options: dict[str, Any],
        selected: Any,
        disabled: bool = False,
    ):

        options = []
        self.setting = setting

        for title, handle in setting_options.items():
            name = title

            option = discord.SelectOption(
                label=name,
                description="",
                value=handle,
                default=(str(handle) == str(selected) or handle == selected),
            )
            options.append(option)

        super().__init__(
            placeholder="Select an Option.",
            min_values=1,
            max_values=1,
            options=options,
            row=1,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: UserSettingView = self.view

        if await view.interaction_check(interaction):
            await view.set_selected_option(interaction, self.values[0])


class SettingsDropdown(discord.ui.Select):

    def __init__(
        self,
        definitions: list[UserSetting],
        selected: UserSettingType | None,
        disabled: bool = False,
    ):

        options = []

        for setting in definitions:
            name = setting.title

            option = discord.SelectOption(
                label=name,
                description=setting.description,
                value=setting.setting_type.value,
                default=(setting.setting_type == selected),
            )
            options.append(option)

        super().__init__(
            placeholder="Select a setting to adjust",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: UserSettingView = self.view

        if await view.interaction_check(interaction):
            selected = None
            if len(self.values) > 0:
                selected = [UserSettingType(value) for value in self.values][0]

            await view.set_selected(interaction, selected)
