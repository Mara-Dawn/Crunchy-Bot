from enum import Enum

import discord

from control.types import UserSettingType
from control.user_settings_manager import UserSettingsManager


class UserSettingsEmbed(discord.Embed):

    def __init__(
        self,
        member: discord.Member,
        user_settings_manager: UserSettingsManager,
        max_width: int = 45,
    ):
        description = "Edit your personal settings here."
        if len(description) < max_width:
            spacing = max_width - len(description)
            description += " " * spacing

        description = f"```python\n{description}```"
        self.user_settings_manager = user_settings_manager
        self.member = member
        self.guild = member.guild

        super().__init__(
            title="User Settings",
            color=discord.Colour.purple(),
            description=description,
        )

        self.set_thumbnail(url=member.display_avatar.url)

    async def load_settings(self):
        for setting_type in UserSettingType:
            title = UserSettingType.get_title(setting_type)
            definition = self.user_settings_manager.get_definition(setting_type)
            value = await self.user_settings_manager.get(
                self.member.id, self.guild.id, setting_type
            )

            if value is not None and definition.options is not None:
                value = list(definition.options.keys())[
                    list(definition.options.values()).index(value)
                ]

            if value is None:
                value = "-"

            if isinstance(value, Enum):
                value = value.value

            self.add_field(name=title, value=value, inline=False)
