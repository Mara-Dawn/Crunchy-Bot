import datetime

from typing import Any, Dict

class UserJail():

    def __init__(
        self,
        guild_id: int,
        member: int,
        jailed_on: datetime.datetime,
        released_on: datetime.datetime = None,
        jail_id: str = None
    ):
        self.guild_id = guild_id
        self.member = member
        self.jailed_on = jailed_on
        self.released_on = released_on
        self.jail_id = jail_id
    
    def get_guild_id(self) -> int:
        return self.guild_id
        
    def get_member_id(self) -> int:
        return self.member
    
    def get_jailed_on_timestamp(self) -> int:
        return int(self.jailed_on.timestamp())
    
    def get_released_on_timestamp(self) -> int:
        return int(self.released_on.timestamp())
    
    def get_jailed_on(self) -> datetime.datetime:
        return self.jailed_on
    
    def get_released_on(self) -> datetime.datetime:
        return self.released_on
    
    def get_id(self) -> int:
        return self.jail_id
    
    @staticmethod
    def from_jail( jail: 'UserJail', released_on: datetime.datetime = None, jail_id: int = None, ) -> 'UserJail':
        
        if jail is None:
            return None
        
        return UserJail(
            jail.get_guild_id(),
            jail.get_member_id(),
            jail.get_jailed_on_timestamp(),
            released_on,
            jail_id
        )
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'UserJail':
        from datalayer.Database import Database
        
        if row is None:
            return None
        
        return UserJail(
            row[Database.JAIL_GUILD_ID_COL],
            row[Database.JAIL_MEMBER_COL],
            datetime.datetime.fromtimestamp(row[Database.JAIL_JAILED_ON_COL]),
            datetime.datetime.fromtimestamp(row[Database.JAIL_RELEASED_ON_COL]) if row[Database.JAIL_RELEASED_ON_COL] is not None else None,
            row[Database.JAIL_ID_COL]
        )