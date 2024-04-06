import datetime
from abc import ABC, abstractmethod
from typing import Any, List
from events.types import EventType


class BotEvent(ABC):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        event_type: EventType,
        event_id: int = None,
    ):
        self.timestamp = timestamp
        self.guild_id = guild_id
        self.type = event_type
        self.event_id = event_id

    def get_timestamp(self) -> int:
        return int(self.timestamp.timestamp())

    def get_datetime(self) -> datetime.datetime:
        return self.timestamp

    def get_guild_id(self) -> int:
        return self.guild_id

    def get_type(self) -> EventType:
        return self.type

    def get_id(self) -> int:
        return self.event_id

    @abstractmethod
    def get_causing_user_id(self) -> int:
        pass

    @abstractmethod
    def get_type_specific_args(self) -> List[Any]:
        pass
