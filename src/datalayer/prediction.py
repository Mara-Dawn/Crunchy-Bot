import datetime
from typing import Any

from datalayer.types import PredictionState


class Prediction:

    def __init__(
        self,
        guild_id: int,
        author_id: int,
        content: str,
        outcomes: dict[int, str],
        state: PredictionState,
        moderator_id: int = None,
        lock_datetime: datetime.datetime = None,
        comment: str = None,
        id: str = None,
    ):
        self.guild_id = guild_id
        self.author_id = author_id
        self.content = content
        self.state = state
        self.outcomes = outcomes
        self.moderator_id = moderator_id
        self.lock_datetime = lock_datetime
        self.comment = comment
        self.id = id

    def get_timestamp_sort(self) -> float:
        if self.lock_datetime is None:
            max_date = datetime.datetime.max
            return max_date.replace(tzinfo=datetime.UTC).timestamp()
        return int(self.lock_datetime.timestamp())

    def get_timestamp(self) -> float:
        if self.lock_datetime is None:
            return None
        return int(self.lock_datetime.timestamp())

    @staticmethod
    def from_db_row(
        row: dict[str, Any], outcome_rows: list[dict[str, Any]]
    ) -> "Prediction":
        from datalayer.database import Database

        if row is None:
            return None
        outcomes = {}
        for outcome in outcome_rows:
            outcomes[outcome[Database.PREDICTION_OUTCOME_ID_COL]] = outcome[
                Database.PREDICTION_OUTCOME_CONTENT_COL
            ]

        lock_timestamp = None
        if row[Database.PREDICTION_LOCK_TIMESTAMP_COL] is not None:
            lock_timestamp = datetime.datetime.fromtimestamp(
                row[Database.PREDICTION_LOCK_TIMESTAMP_COL]
            )

        return Prediction(
            guild_id=row[Database.PREDICTION_GUILD_ID_COL],
            author_id=row[Database.PREDICTION_AUTHOR_COL],
            content=row[Database.PREDICTION_CONTENT_COL],
            state=PredictionState(row[Database.PREDICTION_STATE_COL]),
            outcomes=outcomes,
            moderator_id=row[Database.PREDICTION_MOD_ID_COL],
            lock_datetime=lock_timestamp,
            comment=row[Database.PREDICTION_COMMENT_COL],
            id=row[Database.PREDICTION_ID_COL],
        )
