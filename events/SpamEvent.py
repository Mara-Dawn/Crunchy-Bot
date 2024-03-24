import datetime

from typing import Any, Dict
from events.BotEvent import BotEvent
from events.EventType import EventType

class SpamEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member: int,
        event_id: int = None
    ):
        super().__init__(timestamp, guild_id, EventType.SPAM, event_id)
        self.member = member
        
    def get_member(self) -> int:
        return self.member
     
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'SpamEvent':
        from datalayer.Database import Database
        if row is None:
            return None
        
        return SpamEvent(
            timestamp = datetime.datetime.fromtimestamp(row[Database.EVENT_TIMESTAMP_COL]),
            guild_id = row[Database.EVENT_GUILD_ID_COL],
            member = row[Database.SPAM_EVENT_MEMBER_COL],
            event_id = row[Database.EVENT_ID_COL]
        )
        