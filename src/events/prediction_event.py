import datetime
from typing import Any

from events.bot_event import BotEvent
from events.types import EventType, PredictionEventType


class PredictionEvent(BotEvent):

    def __init__(
        self,
        timestamp: datetime.datetime,
        guild_id: int,
        prediction_id: int,
        member_id: int,
        prediction_event_type: PredictionEventType,
        outcome_id: int = None,
        amount: int = None,
        id: int = None,
    ):
        super().__init__(timestamp, guild_id, EventType.PREDICTION, id)
        self.prediction_id = prediction_id
        self.member_id = member_id
        self.prediction_event_type = prediction_event_type
        self.outcome_id = outcome_id
        self.amount = amount

    def get_causing_user_id(self) -> int:
        return self.member_id

    def get_type_specific_args(self) -> list[Any]:
        return [
            self.prediction_id,
            self.outcome_id,
            self.prediction_event_type,
            self.amount,
        ]

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "PredictionEvent":
        from datalayer.database import Database

        if row is None:
            return None

        return PredictionEvent(
            timestamp=datetime.datetime.fromtimestamp(
                row[Database.EVENT_TIMESTAMP_COL]
            ),
            guild_id=row[Database.EVENT_GUILD_ID_COL],
            prediction_id=row[Database.PREDICTION_EVENT_PREDICTION_ID_COL],
            outcome_id=row[Database.PREDICTION_EVENT_OUTCOME_ID_COL],
            member_id=row[Database.PREDICTION_EVENT_MEMBER_ID_COL],
            prediction_event_type=row[Database.PREDICTION_EVENT_TYPE_COL],
            amount=row[Database.PREDICTION_EVENT_AMOUNT_COL],
            id=row[Database.EVENT_ID_COL],
        )
