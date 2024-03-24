from enum import Enum

class EventType(str, Enum):
    INTERACTION = 'interaction'
    JAIL = 'jail'
    TIMEOUT = 'timeout'
    QUOTE = 'quote'
    SPAM = 'spam'
    BEANS = 'beans'