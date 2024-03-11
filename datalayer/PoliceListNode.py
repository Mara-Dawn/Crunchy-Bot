import collections
import datetime
import itertools

class PoliceListNode():
    
    def __init__(self, author_id: int):
        self.author_id = author_id
        self.spam_message_queue = collections.deque(maxlen=50)
        self.timeout_message_queue = collections.deque(maxlen=50)
        self.timeout_flag = False
    
    def __threshold_check(self, queue: collections.deque, interval: int,  limit: int, offset: int = 0) -> bool:
        if len(queue) < (limit + offset):
            return False
        
        min_time = datetime.datetime.max
        max_time = datetime.datetime.min
        
        slice_start = len(queue) - (limit + offset)
        slice_end = len(queue) - offset
        
        slice = list(itertools.islice(queue, slice_start, slice_end))
        
        for timestamp in slice:
            min_time = min([min_time, timestamp.replace(tzinfo=None)])
            max_time = max([max_time, timestamp.replace(tzinfo=None)]) 
        
        difference = max_time - min_time
        return difference.total_seconds() < interval
    
    def track_spam_message(self, message_timestamp: datetime.datetime) -> None:
        self.spam_message_queue.append(message_timestamp)
    
    def track_timeout_message(self, message_timestamp: datetime.datetime) -> None:
        self.timeout_message_queue.append(message_timestamp)
    
    def spam_check(self, interval: int,  limit: int, offset: int = 0) -> bool:
        return self.__threshold_check(self.spam_message_queue, interval, limit, offset)
    
    def check_spam_score_increase(self, interval: int, limit: int) -> bool:
        # only returns true for every limit'th message the user was spamming in a row
        offset = 0
        while self.spam_check(interval, limit, offset):
            offset += 1
        
        return offset == 1 or (offset - 1) % limit == 0
    
    def timeout_check(self, interval: int,  limit: int) -> bool:
        return self.__threshold_check(self.timeout_message_queue, interval, limit, 0)
    
    def is_in_timeout(self) -> datetime.datetime:
        return self.timeout_flag

    def set_timeout_flag(self) -> None:
        self.timeout_flag = True
        
    def release(self) -> None:
        self.timeout_flag = False
        self.timeout_message_queue.clear()