import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType


class NotificationEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        message: str,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.NOTIFICATION, id)
        self.message = message

    def get_causing_user_id(self) -> int:
        return 0

    def get_type_specific_args(self) -> list[Any]:
        return []
