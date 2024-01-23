
import datetime
from datalayer import UserInteraction

from events.BotEvent import BotEvent
from events.EventType import EventType

class InteractionEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        interaction_type: UserInteraction,
        from_user: int,
        to_user: int
    ):
        super().__init__(timestamp, guild_id, EventType.INTERACTION)
        self.interaction_type = interaction_type
        self.from_user = from_user
        self.to_user = to_user
        
    def get_interaction_type(self) -> UserInteraction:
        return self.interaction_type
     
    def get_from_user(self) -> int:
        return self.from_user
    
    def get_to_user(self) -> int:
        return self.to_user