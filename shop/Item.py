import datetime
from typing import Any, Dict

class Item():

    def __init__(
        self,
        name: str, 
        type: int,
        description: str,
        emoji: str,
        cost: int
    ):
        self.name = name
        self.type = type
        self.description = description
        self.cost = cost
        self.emoji = emoji
     
    def get_name(self) -> str:
        return self.name
    
    def get_type(self) -> int:
        return self.type
    
    def get_description(self) -> str:
        return self.description
    
    def get_emoji(self) -> str:
        return self.emoji
    
    def get_cost(self) -> int:
        return self.cost
    
    def handle() -> None:
        pass