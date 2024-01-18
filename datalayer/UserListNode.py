import collections
import datetime
from typing import List

class UserListNode():
    
    def __init__(self, author_id: int, timestamp: datetime.datetime, queue_size: int = 4):
        self.author_id = author_id
        self.timeout_timestamp = timestamp
        self.message_queue = collections.deque(5*[datetime.datetime], queue_size)
        self.notified = False
    
    def add_message(self, message_timestamp: datetime.datetime) -> None:
        self.message_queue.append(message_timestamp)
        
    def get_message_diff(self) -> float:
        min_time = False
        max_time = False
        for timestamp in self.message_queue:
            min_time = min(min_time, timestamp) if min_time else timestamp
            max_time = max(max_time, timestamp) if max_time else timestamp
        if not min_time or not max_time:
            return 0
        difference = max_time - min_time
        return difference.total_seconds()
        
    def notify(self) -> None:
        self.notified = True;

    def was_notified(self) -> bool:
        return self.notified
    
    def get_timestamp(self) -> datetime.datetime:
        return self.timeout_timestamp

    def set_timestamp(self, timestamp: datetime.datetime) -> None:
        self.timeout_timestamp = timestamp