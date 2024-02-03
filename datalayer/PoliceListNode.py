import collections
import datetime
import itertools

class PoliceListNode():
    
    def __init__(self, author_id: int, queue_size: int):
        self.author_id = author_id
        self.queue_size = queue_size
        self.message_queue = collections.deque(maxlen=queue_size)
        self.timeout_flag = False
    
    def add_message(self, message_timestamp: datetime.datetime) -> None:
        self.message_queue.append(message_timestamp)
        
    def is_spamming(self, interval: int,  limit: int, offset: int = 0) -> bool:
        if len(self.message_queue) < (limit + offset):
            return False
        
        min_time = datetime.datetime.max
        max_time = datetime.datetime.min
        
        slice_start = len(self.message_queue) - (limit + offset)
        slice_end = len(self.message_queue) - offset - 1
        
        slice = list(itertools.islice(self.message_queue, slice_start, slice_end))
        
        for timestamp in slice:
            min_time = min([min_time, timestamp.replace(tzinfo=None)])
            max_time = max([max_time, timestamp.replace(tzinfo=None)]) 
        
        difference = max_time - min_time
        return difference.total_seconds() < interval
    
    def check_spam_score_increase(self, interval: int, limit: int) -> bool:
        # only returns true for every limit'th message the user was spamming in a row
        offset = 0
        while self.is_spamming(interval, limit, offset):
            offset += 1
        
        return offset == 1 or (offset - 1) % limit == 0
    
    def is_in_timeout(self) -> datetime.datetime:
        return self.timeout_flag

    def timeout(self) -> None:
        self.timeout_flag = True
        
    def release(self) -> None:
        self.timeout_flag = False
        self.message_queue.clear()