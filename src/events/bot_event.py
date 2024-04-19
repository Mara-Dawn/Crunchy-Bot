import datetime
from abc import ABC, abstractmethod
from typing import Any

from events.types import EventType


class BotEvent(ABC):

    def __init__(
        self,
        datetime: datetime.datetime,
        guild_id: int,
        event_type: EventType,
        id: int = None,
    ):
        self.datetime = datetime
        self.guild_id = guild_id
        self.type = event_type
        self.id = id

    def get_timestamp(self) -> int:
        return int(self.datetime.timestamp())

    @abstractmethod
    def get_causing_user_id(self) -> int:
        pass

    @abstractmethod
    def get_type_specific_args(self) -> list[Any]:
        pass
