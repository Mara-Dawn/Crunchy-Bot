import datetime

from typing import Any, Dict
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
        to_user: int,
        event_id: int = None
    ):
        super().__init__(timestamp, guild_id, EventType.INTERACTION, event_id)
        self.interaction_type = interaction_type
        self.from_user = from_user
        self.to_user = to_user
        
    def get_interaction_type(self) -> UserInteraction:
        return self.interaction_type
     
    def get_from_user(self) -> int:
        return self.from_user
    
    def get_to_user(self) -> int:
        return self.to_user
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'InteractionEvent':
        from datalayer.Database import Database
        if row is None:
            return None
        
        return InteractionEvent(
            timestamp = datetime.datetime.fromtimestamp(row[Database.EVENT_TIMESTAMP_COL]),
            guild_id = row[Database.EVEN_GUILD_ID_COL],
            interaction_type = row[Database.INTERACTION_EVENT_TYPE_COL],
            from_user = row[Database.INTERACTION_EVENT_FROM_COL],
            to_user = row[Database.INTERACTION_EVENT_TO_COL],
            event_id = row[Database.EVENT_ID_COL]
        )