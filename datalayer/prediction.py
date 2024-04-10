from typing import Any  # noqa: UP035


class Prediction:

    def __init__(
        self,
        guild_id: int,
        author_id: int,
        content: str,
        outcomes: list[str],
        approved: bool = False,
        id: str = None,
    ):
        self.guild_id = guild_id
        self.author_id = author_id
        self.content = content
        self.approved = approved
        self.outcomes = outcomes
        self.id = id

    @staticmethod
    def from_db_row(
        row: dict[str, Any], outcome_rows: list[dict[str, Any]]
    ) -> "Prediction":
        from datalayer.database import Database

        if row is None:
            return None
        outcomes = []
        for outcome in outcome_rows:
            outcomes.append(outcome[Database.PREDICTION_OUTCOME_CONTENT_COL])

        return Prediction(
            guild_id=row[Database.PREDICTION_GUILD_COL],
            author_id=row[Database.PREDICTION_AUTHOR_COL],
            content=row[Database.PREDICTION_CONTENT_COL],
            approved=row[Database.PREDICTION_APPROVED_COL],
            outcomes=outcomes,
            id=row[Database.PREDICTION_ID_COL],
        )
