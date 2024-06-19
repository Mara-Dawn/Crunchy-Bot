import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType


class KarmaEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        amount: int,
        recipient_id: int,
        giver_id: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.KARMA, id)
        self.amount = amount
        self.recipient_id = recipient_id
        self.giver_id = giver_id

    def get_causing_user_id(self) -> int:
        return self.giver_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.recipient_id, self.amount]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "KarmaEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return KarmaEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            recipient_id=row[Database.KARMA_EVENT_RECIPIENT_ID],
            amount=row[Database.KARMA_EVENT_AMOUNT],
            giver_id=row[Database.KARMA_EVENT_GIVER_ID],
            id=row[Database.EVENT_ID_COL],
        )
