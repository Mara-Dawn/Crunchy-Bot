
import datetime
from typing import List

from BotUtil import BotUtil
from datalayer.UserInteraction import UserInteraction

class JailListNode():
    
    def __init__(self, user_id: int, timestamp: datetime.datetime, duration: int):
        
        self.user_id = user_id
        self.timestamp = timestamp
        self.duration = duration
        self.release_timestamp = timestamp + datetime.timedelta(minutes=duration) 
        self.jail_id: int = None

    
    def gt_user_id(self) -> int:
        
        return self.user_id
    
    def get_duration(self) -> int:
        
        return self.duration
    
    def get_duration_str(self) -> int:
        
        return BotUtil.strfdelta(self.duration, inputtype="minutes")
    
    def set_jail_id(self, id: int):
        
        self.jail_id = id
        
    def get_jail_id(self) -> int:
        
        return self.jail_id
    
    def add_to_duration(self, amount: int) -> None:
        
        self.duration += amount
        self.release_timestamp = self.timestamp + datetime.timedelta(minutes=self.duration) 
    
    def get_timestamp(self) -> datetime.datetime:
        
        return self.timestamp
    
    def get_release_timestamp(self) -> datetime.datetime:
        
        return self.release_timestamp
    
    def get_remaining(self) -> float:
        
        remainder = self.release_timestamp - datetime.datetime.now()
        return remainder.total_seconds()
    
    def get_remaining_str(self) -> float:
        
        remainder = self.release_timestamp - datetime.datetime.now()
        
        return BotUtil.strfdelta(remainder)
    
        