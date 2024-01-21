
import datetime
from typing import List

from BotUtil import BotUtil

class JailListNode():
    
    def __init__(self, user_id: int, timestamp: datetime.datetime, duration: int):
        
        self.user_id = user_id
        self.timestamp = timestamp
        self.duration = duration
        self.release_timestamp = timestamp + datetime.timedelta(minutes=duration) 
        
        self.slappers: List[int] = []
        self.petters: List[int] = []
        self.farters: List[int] = []

    
    def gt_user_id(self) -> int:
        
        return self.user_id
    
    def get_duration(self) -> int:
        
        return self.duration
    
    def get_duration_str(self) -> int:
        
        return BotUtil.strfdelta(self.duration, inputtype="minutes")
    
    def add_slapper(self, user_id: int) -> None:
        
        if user_id not in self.slappers:
            self.slappers.append(user_id)
            
    def add_petter(self, user_id: int) -> None:
        
        if user_id not in self.petters:
            self.petters.append(user_id)
            
    def add_farter(self, user_id: int) -> None:
        
        if user_id not in self.farters:
            self.farters.append(user_id)
            
    def get_slappers(self) -> List[int]:
        
        return self.slappers

    def get_petters(self) -> List[int]:
        
        return self.petters
    
    def get_farters(self) -> List[int]:
        
        return self.farters
    
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