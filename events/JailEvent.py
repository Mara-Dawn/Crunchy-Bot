
import datetime

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
        jail_reference: int
    ):
        super().__init__(timestamp, guild_id, EventType.JAIL)
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

    def get_jail_reference(self) -> int:
        return self.jail_reference