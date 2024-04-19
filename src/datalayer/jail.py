import datetime
from typing import Any


class UserJail:

    def __init__(
        self,
        guild_id: int,
        member_id: int,
        jailed_on: datetime.datetime,
        released_on: datetime.datetime = None,
        id: int = None,
    ):
        self.guild_id = guild_id
        self.member_id = member_id
        self.jailed_on = jailed_on
        self.released_on = released_on
        self.id = id

    def get_jailed_on_timestamp(self) -> int:
        return int(self.jailed_on.timestamp())

    def get_released_on_timestamp(self) -> int:
        return int(self.released_on.timestamp())

    @staticmethod
    def from_jail(
        jail: "UserJail",
        released_on: datetime.datetime = None,
        jail_id: int = None,
    ) -> "UserJail":

        if jail is None:
            return None

        return UserJail(
            jail.guild_id,
            jail.member_id,
            jail.jailed_on,
            released_on,
            jail_id,
        )

    @staticmethod
    def from_db_row(row: dict[str, Any]) -> "UserJail":
        from datalayer.database import Database

        if row is None:
            return None

        return UserJail(
            row[Database.JAIL_GUILD_ID_COL],
            row[Database.JAIL_MEMBER_COL],
            datetime.datetime.fromtimestamp(row[Database.JAIL_JAILED_ON_COL]),
            (
                datetime.datetime.fromtimestamp(row[Database.JAIL_RELEASED_ON_COL])
                if row[Database.JAIL_RELEASED_ON_COL] is not None
                else None
            ),
            row[Database.JAIL_ID_COL],
        )
