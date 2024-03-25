from typing import List
from datalayer.Database import Database
from datalayer.ModuleSettings import ModuleSettings
from datalayer.GuildSettings import GuildSettings
from BotLogger import BotLogger
from discord.ext import commands

class BotSettings():

    DEFAULT_KEY = "defaults"
    
    POLICE_SUBSETTINGS_KEY = "police"
    POLICE_ENABLED_KEY = "police_enabled"
    POLICE_NAUGHTY_ROLES_KEY = "naughty_roles"
    POLICE_TIMEOUT_LENGTH_KEY = "timeout"
    POLICE_TIMEOUT_NOTICE_KEY = "timeout_notice"
    POLICE_MESSAGE_LIMIT_KEY = "message_limit"
    POLICE_MESSAGE_LIMIT_INTERVAL_KEY = "message_limit_interval"
    POLICE_EXCLUDED_CHANNELS_KEY = "untracked_channels"
    POLICE_TIMEOUTS_BEFORE_JAIL_KEY = "timeouts_before_jail"
    POLICE_TIMEOUT_JAIL_DURATION_KEY = "timeout_jail_duration"
    
    
    JAIL_SUBSETTINGS_KEY = "jail"
    JAIL_ENABLED_KEY = "jail_enabled"
    JAIL_CHANNELS_KEY = "jail_channel"
    JAIL_ROLE_KEY = "jail_role"
    JAIL_SLAP_TIME_KEY = "slap_time"
    JAIL_PET_TIME_KEY = "pet_time"
    JAIL_FART_TIME_MAX_KEY = "fart_time_max"
    JAIL_FART_TIME_MIN_KEY = "fart_time_min"
    JAIL_BASE_CRIT_RATE_KEY = "base_crit_rate"
    JAIL_BASE_CRIT_MOD_KEY = "base_crit_mod"
    JAIL_MOD_ROLES_KEY = "moderator_roles"
    
    BEANS_SUBSETTINGS_KEY = "beans"
    BEANS_ENABLED_KEY = "beans_enabled"
    BEANS_CHANNELS_KEY = "beans_channels"
    BEANS_DAILY_MIN = "beans_daily_min"
    BEANS_DAILY_MAX = "beans_daily_max"
    BEANS_GAMBA_COST = "beans_gamba_amount"
    BEANS_GAMBA_COOLDOWN = "beans_gamba_cooldown"
    BEANS_GAMBA_COOLDOWN = "beans_gamba_cooldown"
    
    SHOP_SUBSETTINGS_KEY = "shop"
    SHOP_ENABLED_KEY = "shop_enabled"

    def __init__(self, bot: commands.Bot, database: Database, logger: BotLogger):
        self.logger = logger
        self.bot = bot
        self.database = database
        
        # defaults
        police_settings = ModuleSettings(self.POLICE_SUBSETTINGS_KEY, "Police")
        police_settings.add_setting(self.POLICE_ENABLED_KEY, True, "Module Enabled")
        police_settings.add_setting(self.POLICE_NAUGHTY_ROLES_KEY, [], "Roles affected by rate limiting", "handle_roles_value")
        police_settings.add_setting(self.POLICE_TIMEOUT_LENGTH_KEY, 60, "Timeout length in seconds")
        police_settings.add_setting(self.POLICE_TIMEOUT_NOTICE_KEY, "Stop spamming, bitch!", "Message sent to timed out users")
        police_settings.add_setting(self.POLICE_MESSAGE_LIMIT_KEY, 4, "Number of messages before timeout")
        police_settings.add_setting(self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY, 10, "Interval for counting messages before timeout")
        police_settings.add_setting(self.POLICE_EXCLUDED_CHANNELS_KEY, [], "Channels excluded from rate limit checks", "handle_channels_value")
        police_settings.add_setting(self.POLICE_TIMEOUTS_BEFORE_JAIL_KEY, 5, "Number of timeouts before jail")
        police_settings.add_setting(self.POLICE_TIMEOUT_JAIL_DURATION_KEY, 30, "Jail duration")
        
        jail_settings = ModuleSettings(self.JAIL_SUBSETTINGS_KEY, "Jail")
        jail_settings.add_setting(self.JAIL_ENABLED_KEY, True, "Module Enabled")
        jail_settings.add_setting(self.JAIL_CHANNELS_KEY, [], "List of Channels where people can use jail commands to affect jail time.", "handle_channels_value")
        jail_settings.add_setting(self.JAIL_ROLE_KEY, "", "Role for jailed users", "handle_role_value")
        jail_settings.add_setting(self.JAIL_MOD_ROLES_KEY, [], "Roles with permission to jail people", "handle_roles_value")
        jail_settings.add_setting(self.JAIL_SLAP_TIME_KEY, 5, "Time increase for each slap in minutes")
        jail_settings.add_setting(self.JAIL_PET_TIME_KEY, 5, "Time reduction for each pet in minutes")
        jail_settings.add_setting(self.JAIL_FART_TIME_MIN_KEY, -10, "Minimum time change from farting in minutes")
        jail_settings.add_setting(self.JAIL_FART_TIME_MAX_KEY, 20, "Maximum time change from farting in minutes")
        jail_settings.add_setting(self.JAIL_BASE_CRIT_RATE_KEY, 0.2, "Chance to critically hit a fart etc")
        jail_settings.add_setting(self.JAIL_BASE_CRIT_MOD_KEY, 2, "Crit Multiplier")
        
        beans_settings = ModuleSettings(self.BEANS_SUBSETTINGS_KEY, "Beans")
        beans_settings.add_setting(self.BEANS_ENABLED_KEY, True, "Module Enabled")
        beans_settings.add_setting(self.BEANS_CHANNELS_KEY, [], "Channels for bean commands", "handle_channels_value")
        beans_settings.add_setting(self.BEANS_DAILY_MIN, 10, "Mininum daily beans granted to users")
        beans_settings.add_setting(self.BEANS_DAILY_MAX, 25, "Maximum daily beans granted to users")
        beans_settings.add_setting(self.BEANS_GAMBA_COST, 10, "Amount of beans spent on each gamba attempt")
        beans_settings.add_setting(self.BEANS_GAMBA_COOLDOWN, 10, "Amount of minutes between gamba attempts")
        
        shop_settings = ModuleSettings(self.SHOP_SUBSETTINGS_KEY, "Beans Shop")
        shop_settings.add_setting(self.SHOP_ENABLED_KEY, True, "Module Enabled")
        
        self.settings = GuildSettings()
        self.settings.add_module(police_settings)
        self.settings.add_module(jail_settings)
        self.settings.add_module(beans_settings)
        self.settings.add_module(shop_settings)
        
    def __update_setting(self, guild: int, cog: str, key: str, value) -> None:
        self.database.update_setting(guild, cog, key, value)
                       
    def __get_setting(self, guild: int, cog: str, key: str):
        result = self.database.get_setting(guild, cog, key)
        
        if result is not None:
            return result
        
        return self.settings.get_default_setting(cog, key)
    
    def get_setting_title(self, cog: str, key: str):
        result = self.settings.get_module(cog)

        if result is None:
             return None
        
        module = result.get_setting(key)

        if module is None:
            return None
        
        return module.get_title()
    
    def handle_roles_value(self, guild_id: int, roles: List[int]) -> str:
        return " " + ", ".join([self.handle_role_value(guild_id, id) for id in roles]) + " "

    def handle_role_value(self, guild_id: int, role: int) -> str:
        guild_obj = self.bot.get_guild(guild_id)
        return guild_obj.get_role(role).name if guild_obj.get_role(role) is not None else " "
    
    def handle_channels_value(self, guild_id: int, channels: List[int]) -> str:
        guild_obj = self.bot.get_guild(guild_id)
        return " " + ", ".join([guild_obj.get_channel(id).name for id in channels]) + " "
        
    def get_settings_string(self, guild: int, cog: str = "") -> str:
        guild_obj = self.bot.get_guild(guild)
        
        indent = '    '
        output = f'# Settings for {guild_obj.name}:\n'
        
        modules = self.settings.get_modules()
        
        for module_key in modules:
            
            if cog != "" and module_key != cog:
                continue
            
            module_settings = modules[module_key].get_settings()
            output += f'\n## Module: {modules[module_key].get_name()}\n'
            
            for setting_key in module_settings:
                
                setting = module_settings[setting_key]
                value = self.__get_setting(guild, module_key, setting_key)
                
                if setting.get_handler() != "":
                    handler = getattr(self, setting.get_handler())
                    value = handler(guild, value)
                
                output += f'{indent}{setting.get_title()}: `{value}`\n'
                
        return output

    # Police Settings

    def get_police_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_ENABLED_KEY)
    
    def set_police_enabled(self, guild: int, enabled: bool) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_ENABLED_KEY, enabled)
        
    def get_police_naughty_roles(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY)]
    
    def set_police_naughty_roles(self, guild: int, roles: List[int]) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
        
    def add_police_naughty_role(self, guild: int, role: int) -> None:
        roles = self.get_police_naughty_roles(guild)
        if role not in roles: roles.append(role)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
        
    def remove_police_naughty_role(self, guild: int, role: int) -> None:
        roles = self.get_police_naughty_roles(guild)
        if role in roles: roles.remove(role)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
    
    def get_police_exclude_channels(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_EXCLUDED_CHANNELS_KEY)]
    
    def set_police_exclude_channels(self, guild: int, channels: List[int]) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_EXCLUDED_CHANNELS_KEY, channels)
    
    def add_police_exclude_channel(self, guild: int, channel: int) -> None:
        channels = self.get_police_exclude_channels(guild)
        if channel not in channels: channels.append(channel)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_EXCLUDED_CHANNELS_KEY, channels)
        
    def remove_police_exclude_channel(self, guild: int, channel: int) -> None:
        channels = self.get_police_exclude_channels(guild)
        if channel in channels: channels.remove(channel)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_EXCLUDED_CHANNELS_KEY, channels)
    
    def get_police_timeout(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_LENGTH_KEY))
    
    def set_police_timeout(self, guild: int, timeout: int) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_LENGTH_KEY, timeout)
    
    def get_police_timeout_notice(self, guild: int) -> str:
        return self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_NOTICE_KEY)
    
    def set_police_timeout_notice(self, guild: int, message: str) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_NOTICE_KEY, message)
        
    def get_police_message_limit(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_KEY))
    
    def set_police_message_limit(self, guild: int, limit: int) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_KEY, limit)
        
    def get_police_message_limit_interval(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY))
    
    def set_police_message_limit_interval(self, guild: int, interval: int) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY, interval)
    
    def get_police_timeouts_before_jail(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUTS_BEFORE_JAIL_KEY))
    
    def set_police_timeouts_before_jail(self, guild: int, amount: int) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUTS_BEFORE_JAIL_KEY, amount)
        
    def get_police_timeout_jail_duration(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_JAIL_DURATION_KEY))
    
    def set_police_timeout_jail_duration(self, guild: int, duration: int) -> None:
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_JAIL_DURATION_KEY, duration)
    
    # Jail Settings
    
    def get_jail_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_ENABLED_KEY)
    
    def set_jail_enabled(self, guild: int, enabled: bool) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_ENABLED_KEY, enabled)
        
    def get_jail_role(self, guild: int) -> int:
        value = self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_ROLE_KEY)
        return int(value) if value != '' else 0
    
    def set_jail_role(self, guild: int, role_id: int) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_ROLE_KEY, role_id)
        
    def get_jail_channels(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_CHANNELS_KEY)]
    
    def set_jail_channels(self, guild: int, channels: List[int]) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_CHANNELS_KEY, channels)
    
    def add_jail_channel(self, guild: int, channel: int) -> None:
        channels = self.get_jail_channels(guild)
        if channel not in channels: channels.append(channel)
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_CHANNELS_KEY, channels)
        
    def remove_jail_channel(self, guild: int, channel: int) -> None:
        channels = self.get_jail_channels(guild)
        if channel in channels: channels.remove(channel)
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_CHANNELS_KEY, channels)
        
    def get_jail_slap_time(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_SLAP_TIME_KEY))
    
    def set_jail_slap_time(self, guild: int, time: int) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_SLAP_TIME_KEY, time)
        
    def get_jail_pet_time(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_PET_TIME_KEY))
    
    def set_jail_pet_time(self, guild: int, time: int) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_PET_TIME_KEY, time)
        
    def get_jail_fart_min(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_FART_TIME_MIN_KEY))
    
    def set_jail_fart_min(self, guild: int, time: int) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_FART_TIME_MIN_KEY, time)
    
    def get_jail_fart_max(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_FART_TIME_MAX_KEY))
    
    def set_jail_fart_max(self, guild: int, time: int) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_FART_TIME_MAX_KEY, time)
        
    def get_jail_base_crit_rate(self, guild: int) -> float:
        return float(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_BASE_CRIT_RATE_KEY))
    
    def set_jail_base_crit_rate(self, guild: int, rate: float) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_BASE_CRIT_RATE_KEY, rate)
    
    def get_jail_base_crit_mod(self, guild: int) -> float:
        return float(self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_BASE_CRIT_MOD_KEY))
    
    def set_jail_base_crit_mod(self, guild: int, mod: float) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_BASE_CRIT_MOD_KEY, mod)
    
    def get_jail_mod_roles(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_MOD_ROLES_KEY)]
    
    def set_jail_mod_roles(self, guild: int, roles: List[int]) -> None:
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_MOD_ROLES_KEY, roles)
    
    def add_jail_mod_role(self, guild: int, role: int) -> None:
        roles = self.get_jail_mod_roles(guild)
        if role not in roles: roles.append(role)
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_MOD_ROLES_KEY, roles)
        
    def remove_jail_mod_role(self, guild: int, role: int) -> None:
        roles = self.get_jail_mod_roles(guild)
        if role not in roles: roles.remove(role)
        self.__update_setting(guild, self.JAIL_SUBSETTINGS_KEY, self.JAIL_MOD_ROLES_KEY, roles)
    
    # Beans Settings
    
    def get_beans_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_ENABLED_KEY)
    
    def set_beans_enabled(self, guild: int, enabled: bool) -> None:
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_ENABLED_KEY, enabled)
        
    def get_beans_daily_min(self, guild: int) -> int:
        return self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_DAILY_MIN)
    
    def set_beans_daily_min(self, guild: int, amount: int) -> None:
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_DAILY_MIN, amount)
        
    def get_beans_daily_max(self, guild: int) -> int:
        return self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_DAILY_MAX)
    
    def set_beans_daily_max(self, guild: int, amount: int) -> None:
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_DAILY_MAX, amount)
        
    def get_beans_gamba_cost(self, guild: int) -> int:
        return self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_GAMBA_COST)
    
    def set_beans_gamba_cost(self, guild: int, amount: int) -> None:
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_GAMBA_COST, amount)
        
    def get_beans_gamba_cooldown(self, guild: int) -> int:
        return self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_GAMBA_COOLDOWN)
    
    def set_beans_gamba_cooldown(self, guild: int, minutes: int) -> None:
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_GAMBA_COOLDOWN, minutes)
    
    def get_beans_channels(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_CHANNELS_KEY)]

    def add_beans_channel(self, guild: int, channel: int) -> None:
        channels = self.get_beans_channels(guild)
        if channel not in channels: channels.append(channel)
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_CHANNELS_KEY, channels)
        
    def remove_beans_channel(self, guild: int, channel: int) -> None:
        channels = self.get_beans_channels(guild)
        if channel in channels: channels.remove(channel)
        self.__update_setting(guild, self.BEANS_SUBSETTINGS_KEY, self.BEANS_CHANNELS_KEY, channels)
    
    # Shop Settings
    
    def get_shop_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.SHOP_SUBSETTINGS_KEY, self.SHOP_ENABLED_KEY)
    
    def set_shop_enabled(self, guild: int, enabled: bool) -> None:
        self.__update_setting(guild, self.SHOP_SUBSETTINGS_KEY, self.SHOP_ENABLED_KEY, enabled)