
import datetime

from events.BotEvent import BotEvent
from events.EventType import EventType

class TimeoutEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member: int,
        duration: int
    ):
        super().__init__(timestamp, guild_id, EventType.TIMEOUT)
        self.member = member
        self.duration = duration
        
    def get_member(self) -> int:
        return self.member
     
    def get_duration(self) -> int:
        return self.duration