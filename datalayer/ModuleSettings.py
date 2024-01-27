from typing import Dict
from datalayer.Setting import Setting

class ModuleSettings():

    def __init__(self, key: str, name: str):
        self.name = name
        self.key = key
        self.settings: Dict[str, Setting] = {}
        
    def get_name(self) -> str:
        return self.name
    
    def get_key(self) -> str:
        return self.key
    
    def add_setting(self, key: str, default, title: str, handler: str ="") -> None:
        self.settings[key] = Setting(self.key, key, default, title, handler)
        
    def get_setting(self, key: str) -> Setting:
        if key not in self.settings.keys():
            return None
        return self.settings[key]
    
    def get_settings(self) -> Dict[str, Setting]:
        return self.settings