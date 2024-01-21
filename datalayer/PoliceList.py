import datetime
from typing import Dict

from datalayer.PoliceListNode import PoliceListNode

class PoliceList():

    def __init__(self):
        self.users: Dict[int, PoliceListNode] = {}

    def add_user(self, author_id: int, message_limit: int) -> None:
        self.users[author_id] = PoliceListNode(author_id, message_limit) 
        
    def add_message(self, user_id: int, message_timestamp: datetime.datetime) -> None:
        self.users[user_id].add_message(message_timestamp)
        
    def remove_user(self, author_id: int) -> None:
        del self.users[author_id]
        
    def clear(self) -> None:
        self.users.clear()

    def get_user(self, author_id: int) -> PoliceListNode:
        return self.users[author_id] if self.has_user(author_id) else PoliceListNode(author_id, datetime.datetime.utcnow())

    def has_user(self, author_id: int) -> bool:
        return author_id in self.users.keys()

    def mark_as_notified(self, author_id: int) -> None:
        self.users[author_id].notify()