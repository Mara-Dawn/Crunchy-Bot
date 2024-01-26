
import datetime

class Quote():

    def __init__(
        self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member: int,
        member_name: str,
        saved_by: int,
        message_id: int,
        message_content: str,
        quote_id: str = None
    ):
        
        self.timestamp = timestamp
        self.guild_id = guild_id
        self.member = member
        self.member_name = member_name
        self.saved_by = saved_by
        self.message_id = message_id
        self.message_content = message_content
        self.quote_id = quote_id 
     
    def get_timestamp(self) -> datetime.datetime:
        return int(self.timestamp.timestamp())
    
    def get_guild_id(self) -> int:
        return self.guild_id
        
    def get_member(self) -> int:
        return self.member
    
    def get_member_name(self) -> str:
        return self.member_name
    
    def get_saved_by(self) -> int:
        return self.saved_by
    
    def get_message_id(self) -> int:
        return self.message_id
    
    def get_message_content(self) -> str:
        return self.message_content
    
    def get_id(self) -> int:
        return self.quote_id
    