
import json
import os

from typing import List
from datalayer.Setting import Setting
from datalayer.ModuleSettings import ModuleSettings
from datalayer.GuildSettings import GuildSettings
from logger import BotLogger
from discord.ext import commands

class BotSettings():

    DEFAULT_KEY = "defaults"
    
    POLICE_SUBSETTINGS_KEY = "police"
    POLICE_ENABLED_KEY = "police_enabled"
    POLICE_NAUGHTY_ROLES_KEY = "naughty_roles"
    POLICE_TIMEOUT_KEY = "timeout"
    POLICE_TIMEOUT_NOTICE_KEY = "timeout_notice"
    POLICE_MESSAGE_LIMIT_KEY = "message_limit"
    POLICE_MESSAGE_LIMIT_INTERVAL_KEY = "message_limit_interval"

    def __init__(self, bot: commands.Bot, logger: BotLogger, file_name: str):
        
        self.file_name = file_name
        self.logger = logger
        self.bot = bot
        
        # defaults
        police_settings = ModuleSettings(self.POLICE_SUBSETTINGS_KEY, "Police")
        police_settings.add_setting(self.POLICE_ENABLED_KEY, True, "Module Enabled")
        police_settings.add_setting(self.POLICE_NAUGHTY_ROLES_KEY, [], "Roles affected by rate limiting", "handle_roles_value")
        police_settings.add_setting(self.POLICE_TIMEOUT_KEY, 60, "Timeout length in seconds")
        police_settings.add_setting(self.POLICE_TIMEOUT_NOTICE_KEY, "Stop spamming, bitch!", "Message sent to timed out users")
        police_settings.add_setting(self.POLICE_MESSAGE_LIMIT_KEY, 3, "Number of messages before timeout")
        police_settings.add_setting(self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY, 10, "Interval for counting messages before timeout")
        
        self.settings = GuildSettings()
        self.settings.add_module(police_settings)
        
        #check if config file exists
        if not os.path.exists(self.file_name):
             
            self.logger.log("init","Creating settings file, using default values")
            
            with open(self.file_name, 'w') as configfile:
                json.dump(self.settings.to_json(), configfile, indent=4)
            
            self.logger.log("init","Settings created successfully")
            return
        
        self.logger.log("init","Load settings from settings.json")
        
        self.__settings_from_file()
        
        self.logger.log("init","Settings loaded")

    def __settings_from_file(self):
        
        with open(self.file_name, 'r+') as configfile:
            data = json.load(configfile)
            self.settings.from_json(data)
    
    def __settings_to_file(self):
        
        with open(self.file_name, 'w') as configfile:
            data = self.settings.to_json()
            configfile.seek(0)
            json.dump(data, configfile, indent=4)
            configfile.truncate()
    
    def __update_setting(self, guild: int, cog: str, key: str, value) -> None:
        
        self.settings.update_setting(guild, cog, key, value)
        self.__settings_to_file()
                       
    def __get_setting(self, guild: int, cog: str, key: str):
        return self.settings.get_guild_setting(guild, cog, key)
    

    def handle_roles_value(self, guild_id: int, roles: List[int]) -> str:
        
        guild_obj = self.bot.get_guild(guild_id)
        return " " + ", ".join([guild_obj.get_role(id).name for id in roles]) + " "
    
    def add_guild(self, guild_id: int) -> None:

        with open(self.file_name, 'r+') as configfile:

            data = json.load(configfile)
            data[guild_id] = self.settings[self.DEFAULT_KEY]
            configfile.seek(0)
            json.dump(data, configfile, indent=4)
            configfile.truncate()
            self.settings = data
            
        self.logger.log(guild_id,  "added save data for guild")

    def remove_guild(self, guild_id: int) -> None:

        with open(self.file_name, "r+") as read_file:
            data = json.load(read_file)
            
            if str(guild_id) in list(data):
                del data[str(guild_id)]
                
            read_file.seek(0)
            json.dump(data, read_file, indent=4)
            read_file.truncate()
            
            self.settings = data
            
        self.logger.log(guild_id,  "cleared savedata for guild")
        
    def get_settings_string(self, guild: int, cog: str = "") -> str:
        
        guild_obj = self.bot.get_guild(guild)
        
        indent = '    '
        output = f'# Settings for {guild_obj.name}:\n'
        
        modules = self.settings.get_modules()
        
        for module_key in modules:
            
            module_settings = modules[module_key].get_settings()
            output += f'\n## Module: {modules[module_key].get_name()}\n'
            
            for setting_key in module_settings:
                
                setting = module_settings[setting_key]
                value = setting.get_value(guild)
                
                if setting.get_handler() != "":
                    handler = getattr(self, setting.get_handler())
                    value = handler(guild, value)
                
                output += f'{indent}{setting.get_title()}: `{value}`\n'
                
        return output

    def get_police_enabled(self, guild: int) -> bool:
        
        return self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_ENABLED_KEY)
    
    def set_police_enabled(self, guild: int, enabled: bool) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_ENABLED_KEY, enabled)
        
    def get_police_naughty_roles(self, guild: int) -> List[int]:
        
        return [int(x) for x in self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY)]
    
    def set_police_naughty_roles(self, guild: int, roles: [int]) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
        
    def add_police_naughty_role(self, guild: int, role: int) -> None:
        
        roles = self.get_police_naughty_roles(guild)
        if role not in roles: roles.append(role)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
        
    def remove_naughty_role(self, guild: int, role: int) -> None:
        
        roles = self.get_police_naughty_roles(guild)
        if role in roles: roles.remove(role)
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_NAUGHTY_ROLES_KEY, roles)
    
    def get_police_timeout(self, guild: int) -> int:
        
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_KEY))
    
    def set_police_timeout(self, guild: int, timeout: int) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_KEY, timeout)
    
    def get_police_timeout_notice(self, guild: int) -> str:
        
        return self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_NOTICE_KEY)
    
    def set_police_timeout_notice(self, guild: int, message: str) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_TIMEOUT_NOTICE_KEY, message)
        
    def get_police_message_limit(self, guild: int) -> int:
        
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_KEY))
    
    def set_police_message_limit(self, guild: int, cog: str, limit: int) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_KEY, limit)
        
    def get_police_message_limit_interval(self, guild: int) -> int:
        
        return int(self.__get_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY))
    
    def set_police_message_limit_interval(self, guild: int, cog: str, interval: int) -> None:
        
        self.__update_setting(guild, self.POLICE_SUBSETTINGS_KEY, self.POLICE_MESSAGE_LIMIT_INTERVAL_KEY, interval)