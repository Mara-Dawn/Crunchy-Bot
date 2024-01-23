import datetime
from typing import Dict, List

from datalayer.JailListNode import JailListNode

class JailList():

    def __init__(self):
        self.users: Dict[int, JailListNode] = {}
        self.delete_users: List[int] = []

    def add_user(self, user_id: int, timestamp: datetime.datetime, duration: int) -> None:
        self.users[user_id] = JailListNode(user_id, timestamp, duration) 
        
    def remove_user(self, user_id: int) -> None:
        del self.users[user_id]
        
    def schedule_removal(self, user_id: int) -> None:
        self.delete_users.append(user_id)
    
    def execute_removal(self) -> None:
        for user in self.delete_users:
            self.remove_user(user)
        
        self.delete_users.clear()
    
    def add_jail_id(self, jail_id: int, user_id: int):
        self.users[user_id].set_jail_id(jail_id)
    
    def clear(self) -> None:
        self.users.clear()

    def get_user(self, user_id: int) -> JailListNode:
        return self.users[user_id] if self.has_user(user_id) else JailListNode(user_id, datetime.datetime.utcnow())

    def get_user_ids(self) -> List[int]:
        return self.users.keys()

    def has_user(self, user_id: int) -> bool:
        return user_id in self.users.keys()