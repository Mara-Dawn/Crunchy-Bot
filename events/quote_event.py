import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType


class QuoteEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        quote_id: str,
        event_id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.QUOTE, event_id)
        self.quote_id = quote_id

    def get_quote_id(self) -> int:
        return self.quote_id

    def get_causing_user_id(self) -> int:
        return 0

    def get_type_specific_args(self) -> list[Any]:
        return []
