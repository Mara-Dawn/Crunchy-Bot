import datetime

class UserListNode():

    def __init__(self, author_id: int, timestamp: datetime.datetime):
        self.author_id = author_id
        self.timestamp = timestamp
        self.notified = False
    
    def notify(self) -> None:
        self.notified = True;

    def was_notified(self) -> bool:
        return self.notified
    
    def get_timestamp(self) -> datetime.datetime:
        return self.timestamp

    def set_timestamp(self, timestamp: datetime.datetime) -> None:
        self.timestamp = timestamp
