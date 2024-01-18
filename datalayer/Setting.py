from typing import List

class Setting():    
    
    def __init__(self, parent_key: str,  key: str, default, title: str, handler: str = ""):
        self.key = key
        self.default = default
        self.title = title
        self.handler = handler
        self.parent_key = parent_key
        
        self.guild_settings = {}
        
    def get_key(self) -> str:
        return self.key

    def get_default(self):
        return self.default
    
    def update(self, guild_id: int, value):
        self.guild_settings[guild_id] = value
        
    def get_value(self, guild_id: int):
        return self.guild_settings[guild_id] if guild_id in self.guild_settings.keys() else self.default
    
    def get_values(self):
        return self.guild_settings
    
    def get_title(self) -> str:
        return self.title
    
    def get_handler(self) -> str:
        return self.handler
    
    def get_parent_key(self) -> str:
        return self.parent_key
