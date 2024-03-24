import datetime

from typing import Any, Dict
from events.BotEvent import BotEvent
from events.EventType import EventType
from events.JailEventType import JailEventType

class JailEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        jail_event_type: JailEventType,
        jailed_by: int,
        duration: int,
        jail_reference: int,
        event_id: int = None
    ):
        super().__init__(timestamp, guild_id, EventType.JAIL, event_id)
        self.jail_event_type = jail_event_type
        self.jailed_by = jailed_by
        self.duration = duration
        self.jail_reference = jail_reference
        
    def get_jail_event_type(self) -> JailEventType:
        return self.jail_event_type
     
    def get_jailed_by(self) -> int:
        return self.jailed_by
     
    def get_duration(self) -> int:
        return self.duration

    def get_jail_id(self) -> int:
        return self.jail_reference
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'JailEvent':
        from datalayer.Database import Database
        if row is None:
            return None
        
        return JailEvent(
            timestamp = datetime.datetime.fromtimestamp(row[Database.EVENT_TIMESTAMP_COL]),
            guild_id = row[Database.EVENT_GUILD_ID_COL],
            jail_event_type = row[Database.JAIL_EVENT_TYPE_COL],
            jailed_by = row[Database.JAIL_EVENT_BY_COL],
            duration = row[Database.JAIL_EVENT_DURATION_COL],
            jail_reference = row[Database.JAIL_EVENT_JAILREFERENCE_COL],
            event_id = row[Database.EVENT_ID_COL]
        )