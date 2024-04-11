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
        id: str = None,
    ):
        self.guild_id = guild_id
        self.author_id = author_id
        self.content = content
        self.state = state
        self.outcomes = outcomes
        self.moderator_id = moderator_id
        self.id = id

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

        return Prediction(
            guild_id=row[Database.PREDICTION_GUILD_ID_COL],
            author_id=row[Database.PREDICTION_AUTHOR_COL],
            content=row[Database.PREDICTION_CONTENT_COL],
            state=row[Database.PREDICTION_STATE_COL],
            outcomes=outcomes,
            moderator_id=row[Database.PREDICTION_MOD_ID_COL],
            id=row[Database.PREDICTION_ID_COL],
        )
