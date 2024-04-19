import datetime
from typing import Any

from datalayer.types import UserInteraction
from events.bot_event import BotEvent
from events.types import EventType


class InteractionEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        interaction_type: UserInteraction,
        from_user_id: int,
        to_user_id: int,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.INTERACTION, id)
        self.interaction_type = interaction_type
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

    def get_causing_user_id(self) -> int:
        return self.from_user_id

    def get_type_specific_args(self) -> list[Any]:
        return [self.to_user_id, self.interaction_type]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "InteractionEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return InteractionEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            interaction_type=row[Database.INTERACTION_EVENT_TYPE_COL],
            from_user_id=row[Database.INTERACTION_EVENT_FROM_COL],
            to_user_id=row[Database.INTERACTION_EVENT_TO_COL],
            id=row[Database.EVENT_ID_COL],
        )
