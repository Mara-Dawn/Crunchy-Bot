import json

from typing import Dict
from datalayer.ModuleSettings import ModuleSettings
from datalayer.Setting import Setting

class GuildSettings():

    def __init__(self):
        self.settings: Dict[str, ModuleSettings] = {}
    
    def add_module(self, module_settings: ModuleSettings) -> ModuleSettings:
        self.settings[module_settings.get_key()] = module_settings
        
    def get_module(self, key: str):
        
        if key not in self.settings.keys():
            return None
        
        return self.settings[key]
    
    def get_modules(self):
        
        return self.settings
    
    def get_setting(self, module: str, setting: str) -> Setting:
        
        if module not in self.settings.keys():
            return None
        
        module_settings = self.settings[module]
        
        return module_settings.get_setting(setting)
    
    def get_guild_setting(self, guild_id: int, module: str, setting: str):
        
        if module not in self.settings.keys():
            return None
        
        module_settings = self.settings[module]
        
        return module_settings.get_setting(setting).get_value(guild_id)

    def update_setting(self, guild_id: int, module: str, key: str, value) -> None:
        
        if module not in self.settings.keys():
            return None
        
        self.settings[module].update_setting(guild_id, key, value)
    
    def to_json(self):
        
        output = {}
        
        for module_key in self.settings:
            
            output[module_key] = {}
            module_settings = self.settings[module_key].get_settings()
            
            for setting_key in module_settings:
                
                output[module_key][setting_key] = {}
                guild_values = module_settings[setting_key].get_values()
                
                for guild_id in guild_values:
                    
                    output[module_key][setting_key][str(guild_id)] = guild_values[guild_id]
        
        return output
    
    def from_json(self, data):
            
        for module_key in data:
            
            module_settings = data[module_key]
            
            for setting_key in module_settings:
                
                guild_values = module_settings[setting_key]
                
                for guild_id in guild_values:
                    
                    self.update_setting(int(guild_id), module_key, setting_key, guild_values[guild_id])