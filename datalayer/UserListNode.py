import collections
import datetime
from typing import List

class UserListNode():
    
    def __init__(self, author_id: int, queue_size: int):
        self.author_id = author_id
        self.timeout_timestamp = None
        self.queue_size = queue_size
        self.message_queue = collections.deque(maxlen=queue_size)
        self.timeout_flag = False
    
    def add_message(self, message_timestamp: datetime.datetime) -> None:
        self.message_queue.append(message_timestamp)
        
    def is_spamming(self, interval: int) -> bool:
        if len(self.message_queue) < self.queue_size:
            return False
        
        min_time = datetime.datetime.max
        max_time = datetime.datetime.min
        for timestamp in self.message_queue:
            min_time = min([min_time, timestamp.replace(tzinfo=None)])
            max_time = max([max_time, timestamp.replace(tzinfo=None)]) 
        
        difference = max_time - min_time
        return difference.total_seconds() < interval
        
    def notify(self) -> None:
        self.notified = True;

    def was_notified(self) -> bool:
        return self.notified
    
    def get_timestamp(self) -> datetime.datetime:
        return self.timeout_timestamp
    
    def is_in_timeout(self) -> datetime.datetime:
        return self.timeout_flag

    def timeout(self, timestamp: datetime.datetime) -> None:
        self.timeout_timestamp = timestamp
        self.timeout_flag = True
        
    def release(self) -> None:
        self.timeout_timestamp = None
        self.timeout_flag = False
        last_msg = self.message_queue.pop()
        self.message_queue.clear()
        self.message_queue.append(last_msg)