import datetime
from typing import Any, Dict

from events.BotEvent import BotEvent
from events.EventType import EventType

class TimeoutEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member: int,
        duration: int,
        event_id: int = None
    ):
        super().__init__(timestamp, guild_id, EventType.TIMEOUT, event_id)
        self.member = member
        self.duration = duration
        
    def get_member(self) -> int:
        return self.member
     
    def get_duration(self) -> int:
        return self.duration
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'TimeoutEvent':
        from datalayer.Database import Database
        if row is None:
            return None
        
        return TimeoutEvent(
            datetime.datetime.fromtimestamp(row[Database.EVENT_TIMESTAMP_COL]),
            row[Database.EVEN_GUILD_ID_COL],
            row[Database.TIMEOUT_EVENT_MEMBER_COL],
            row[Database.TIMEOUT_EVENT_DURATION_COL],
            row[Database.EVENT_ID_COL]
        )
        