import json
import os
from typing import List

from logger import BotLogger

class BotSettings():

    DEFAULT_KEY = "defaults"
    ENABLED_KEY = "enabled"
    NAUGHTY_ROLES_KEY = "naughty_roles"
    TIMEOUT_KEY = "timeout"
    TIMEOUT_NOTICE_KEY = "timeout_notice"
    REFRESH_TIMEOUT_KEY = "refresh_timeout"

    def __init__(self, logger: BotLogger, file_name: str):
        
        self.file_name = file_name
        self.logger = logger
        self.settings = {
            self.DEFAULT_KEY: {
                self.NAUGHTY_ROLES_KEY : [],
                self.TIMEOUT_KEY : 60,
                self.TIMEOUT_NOTICE_KEY : "Stop spamming, bitch!",
                self.REFRESH_TIMEOUT_KEY : False,
                self.ENABLED_KEY : True
            }
        }
        
        #check if config file exists
        if not os.path.exists(self.file_name):
             
            self.logger.log("init","Creating settings file, using default values")
            
            with open(self.file_name, 'w') as configfile:
                json.dump(self.settings, configfile, indent=4)
            
            self.log("init","Settings created successfully")
            return
        
        self.logger.log("init","Load settings from settings.json")
        
        
        with open(self.file_name, 'r+') as configfile:
            data = json.load(configfile)

            # update defaults.
            data[self.DEFAULT_KEY] = self.settings[self.DEFAULT_KEY]
            configfile.seek(0)
            json.dump(data, configfile, indent=4)
            configfile.truncate()

            self.settings = data
        
        self.logger.log("init","Settings loaded")

    def __update_setting(self, guild: int, key: str, value) -> None:

        with open(self.file_name, "r+") as read_file:
            data = json.load(read_file)
            
            guild = str(guild)
            
            # add new guild to data, if missing
            if guild not in list(data):
                newEntry = {}
                data[guild] = newEntry

            data[guild][key] = value
                
            read_file.seek(0)
            json.dump(data, read_file, indent=4)
            read_file.truncate()
            
            self.settings = data
            self.logger.log(guild, "Settings updated: " + str(key) + " = " + str(value))
                       
    def __get_setting(self, guild: int, key: str):

        if str(guild) in list(self.settings) and key in list(self.settings[str(guild)]):
            return self.settings[str(guild)][key]
        else:
            return self.settings[self.DEFAULT_KEY][key]
        

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
        

    def get_naughty_roles(self, guild: int) -> List[int]:
        return [int(x) for x in self.__get_setting(guild, self.NAUGHTY_ROLES_KEY)]
    
    def set_naughty_roles(self, guild: int, roles: [int]):
        self.__update_setting(guild, self.NAUGHTY_ROLES_KEY, roles)
        
    def add_naughty_role(self, guild: int, role: int):
        roles = self.get_naughty_roles(guild)
        if role not in roles: roles.append(role)
        self.__update_setting(guild, self.NAUGHTY_ROLES_KEY, roles)
        
    def remove_naughty_role(self, guild: int, role: int):
        roles = self.get_naughty_roles(guild)
        if role in roles: roles.remove(role)
        self.__update_setting(guild, self.NAUGHTY_ROLES_KEY, roles)
    
    def get_timeout(self, guild: int) -> int:
        return int(self.__get_setting(guild, self.TIMEOUT_KEY))
    
    def set_timeout(self, guild: int, timeout: int):
        self.__update_setting(guild, self.TIMEOUT_KEY, timeout)
    
    def get_timeout_notice(self, guild: int) -> str:
        return self.__get_setting(guild, self.TIMEOUT_NOTICE_KEY)
    
    def set_timeout_notice(self, guild: int, message: str):
        self.__update_setting(guild, self.TIMEOUT_NOTICE_KEY, message)
    
    def get_refresh_timeout_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.REFRESH_TIMEOUT_KEY)
    
    def set_refresh_timeout_enabled(self, guild: int, enabled: bool):
        self.__update_setting(guild, self.REFRESH_TIMEOUT_KEY, enabled)

    def get_enabled(self, guild: int) -> bool:
        return self.__get_setting(guild, self.ENABLED_KEY)
    
    def set_enabled(self, guild: int, enabled: bool):
        self.__update_setting(guild, self.ENABLED_KEY, enabled)