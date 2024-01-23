import collections
import datetime

class PoliceListNode():
    
    def __init__(self, author_id: int, queue_size: int):
        self.author_id = author_id
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
    
    def is_in_timeout(self) -> datetime.datetime:
        return self.timeout_flag

    def timeout(self) -> None:
        self.timeout_flag = True
        
    def release(self) -> None:
        self.timeout_flag = False
        self.message_queue.clear()