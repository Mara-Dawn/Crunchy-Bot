from typing import Dict
from datalayer.ModuleSettings import ModuleSettings

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
    
    def get_default_setting(self, module: str, setting: str):
        if module not in self.settings.keys():
            return None
        
        module_settings = self.settings[module]
        module_setting = module_settings.get_setting(setting)
        if module_setting is None:
            return None
        
        return module_setting.get_default()