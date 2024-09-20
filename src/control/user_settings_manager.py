from typing import Any

from discord.ext import commands

from bot_util import BotUtil
from config import Config
from control.controller import Controller
from control.logger import BotLogger
from control.service import Service
from control.settings_manager import SettingsManager
from control.types import SkillRefreshOption, UserSettingsToggle, UserSettingType
from datalayer.database import Database
from datalayer.settings import UserSetting
from events.bot_event import BotEvent


class UserSettingsManager(Service):

    SETTINGS = {
        UserSettingType.AUTO_SCRAP: UserSetting(
            UserSettingType.AUTO_SCRAP,
            int,
            {f"Loot Level <= {v}": v for v in list(range(0, Config.MAX_LVL))},
            0,
            UserSettingType.get_title(UserSettingType.AUTO_SCRAP),
            "Level of autoscrapped gear (up to and incl.)",
        ),
        UserSettingType.GAMBA_DEFAULT: UserSetting(
            UserSettingType.GAMBA_DEFAULT,
            int,
            None,
            None,
            UserSettingType.get_title(UserSettingType.GAMBA_DEFAULT),
            "Set your default /gamba amount.",
        ),
        UserSettingType.REFRESH_SKILLS: UserSetting(
            UserSettingType.REFRESH_SKILLS,
            SkillRefreshOption,
            {SkillRefreshOption.get_title(v): v for v in SkillRefreshOption},
            SkillRefreshOption.DISABLED,
            UserSettingType.get_title(UserSettingType.REFRESH_SKILLS),
            "Refresh skills automatically after depleting all uses.",
        ),
        UserSettingType.DM_PING: UserSetting(
            UserSettingType.DM_PING,
            UserSettingsToggle,
            {
                "Enabled": UserSettingsToggle.ENABLED,
                "Disabled": UserSettingsToggle.DISABLED,
            },
            UserSettingsToggle.DISABLED,
            UserSettingType.get_title(UserSettingType.DM_PING),
            "Recieve a notification dm after 30s of combat inactivity on your turn.",
        ),
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
        self.log_name = "User Settings"
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

    async def listen_for_event(self, event: BotEvent):
        pass

    def get_definition(self, setting_type: UserSettingType):
        return self.SETTINGS[setting_type]

    async def validate(
        self, guild_id: int, setting_type: UserSettingType, value: Any
    ) -> bool:
        if value is None:
            return False

        setting = self.SETTINGS[setting_type]
        try:
            cast_value = setting.value_type(value)
        except TypeError:
            return False

        match setting_type:
            case (
                UserSettingType.AUTO_SCRAP
                | UserSettingType.REFRESH_SKILLS
                | UserSettingType.DM_PING
            ):
                return cast_value in setting.options.values()
            case UserSettingType.GAMBA_DEFAULT:
                beans_gamba_min = await self.settings_manager.get_beans_gamba_min(
                    guild_id
                )
                beans_gamba_max = await self.settings_manager.get_beans_gamba_max(
                    guild_id
                )
                return cast_value >= beans_gamba_min and cast_value <= beans_gamba_max

    async def get(self, member_id: int, guild_id: int, setting_type: UserSettingType):
        setting = self.SETTINGS[setting_type]
        user_value = await self.database.get_user_setting(
            member_id, guild_id, setting_type
        )
        if user_value is None:
            return setting.default

        try:
            return setting.value_type(user_value)
        except TypeError:
            return user_value

    async def set(
        self, member_id: int, guild_id: int, setting_type: UserSettingType, value: Any
    ):
        if not await self.validate(guild_id, setting_type, value):
            return

        name = BotUtil.get_name(self.bot, guild_id, member_id)

        log_message = f"{name} changed setting {setting_type} to `{value}`."
        self.logger.log(guild_id, log_message, cog=self.log_name)

        return await self.database.set_user_setting(
            member_id, guild_id, setting_type, value
        )
