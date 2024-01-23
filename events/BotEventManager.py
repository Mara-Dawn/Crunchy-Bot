
import datetime
from discord.ext import commands
from BotLogger import BotLogger

from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.InteractionEvent import InteractionEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.TimeoutEvent import TimeoutEvent

class BotEventManager():

    def __init__(self, bot: commands.Bot, settings: BotSettings, database: Database, logger: BotLogger):
        
        self.bot = bot
        self.settings = settings
        self.database = database
        self.logger = logger
        self.log_name = "Events"
        
    def dispatch_interaction_event(self,
        timestamp: datetime.datetime, 
        guild_id: int, 
        interaction_type: UserInteraction,
        from_user: int,
        to_user: int
    ):
        
        event = InteractionEvent(timestamp, guild_id, interaction_type, from_user, to_user)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Interaction event `{interaction_type}` was logged.', self.log_name)
        
    def dispatch_timeout_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        member: int,
        duration: int
    ):
        event = TimeoutEvent(timestamp, guild_id, member, duration)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Timeout event was logged.', self.log_name)
        
    def dispatch_jail_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        jail_event_type: JailEventType,
        jailed_by: int,
        duration: int,
        jail_reference: int
    ):
        event = JailEvent(timestamp, guild_id, jail_event_type, jailed_by, duration, jail_reference)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Jail event `{jail_event_type}` was logged for jail {jail_reference}.', self.log_name)
        
        if jail_event_type is JailEventType.RELEASE:
            self.database.log_jail_release(jail_reference, int(timestamp.timestamp()))
            self.logger.log(guild_id, f'Jail sentence `{jail_reference}` marked as released.', self.log_name)
            
    
    def get_jail_duration(self, jail_id: int) -> int:
        
        events = self.database.get_jail_events(jail_id)
        total_duration = 0
        for event in events:
            total_duration += event[Database.JAIL_EVENT_DURATION_COL]
        
        return total_duration
    
    def has_jail_event(self, jail_id: int, user_id: int, type: JailEventType) -> int:
        
        events = self.database.has_jail_event(jail_id, user_id, type)
        total_duration = 0
        for event in events:
            total_duration += event[Database.JAIL_EVENT_DURATION_COL]
        
        return total_duration