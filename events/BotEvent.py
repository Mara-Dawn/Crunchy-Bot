
import datetime

from events.EventType import EventType


class BotEvent():

    def __init__(self,timestamp: datetime.datetime, guild_id: int, type: EventType):
        self.timestamp = timestamp
        self.guild_id = guild_id
        self.type = type
     
    def get_timestamp(self) -> datetime.datetime:
        return int(self.timestamp.timestamp())
    
    def get_guild_id(self) -> int:
        return self.guild_id
    
    def get_type(self) -> EventType:
        return self.type