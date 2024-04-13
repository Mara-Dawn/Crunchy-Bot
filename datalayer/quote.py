import datetime
from typing import Any  # noqa: UP035


class Quote:

    def __init__(
        self,
        datetime: datetime.datetime,
        guild_id: int,
        member_id: int,
        member_name: str,
        saved_by: int,
        message_id: int,
        channel_id: int,
        message_content: str,
        id: str = None,
    ):
        self.datetime = datetime
        self.guild_id = guild_id
        self.member_id = member_id
        self.member_name = member_name
        self.saved_by = saved_by
        self.message_id = message_id
        self.channel_id = channel_id
        self.message_content = message_content
        self.id = id

    def get_timestamp(self) -> float:
        return int(self.datetime.timestamp())

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "Quote":
        from datalayer.database import Database

        if row is None:
            return None

        return Quote(
            datetime=datetime.datetime.fromtimestamp(row[Database.QUOTE_TIMESTAMP_COL]),
            guild_id=row[Database.QUOTE_GUILD_COL],
            member_id=row[Database.QUOTE_MEMBER_COL],
            member_name=row[Database.QUOTE_MEMBER_NAME_COL],
            saved_by=row[Database.QUOTE_SAVED_BY_COL],
            message_id=row[Database.QUOTE_MESSAGE_COL],
            channel_id=row[Database.QUOTE_CHANNEL_COL],
            message_content=row[Database.QUOTE_TEXT_COL],
            id=row[Database.QUOTE_ID_COL],
        )
