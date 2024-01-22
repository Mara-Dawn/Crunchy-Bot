from typing import List

class Setting():    
    
    def __init__(self, parent_key: str,  key: str, default, title: str, handler: str = ""):
        self.key = key
        self.default = default
        self.title = title
        self.handler = handler
        self.parent_key = parent_key
        
    def get_key(self) -> str:
        return self.key

    def get_default(self):
        return self.default
    
    def get_title(self) -> str:
        return self.title
    
    def get_handler(self) -> str:
        return self.handler
    
    def get_parent_key(self) -> str:
        return self.parent_key
