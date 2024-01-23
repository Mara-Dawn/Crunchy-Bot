
import datetime
from discord.ext import commands

from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.InteractionEvent import InteractionEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.TimeoutEvent import TimeoutEvent

class BotEventManager():

    def __init__(self, bot: commands.Bot, settings: BotSettings, database: Database):
        
        self.bot = bot
        self.settings = settings
        self.database = database
        
    def create_interaction_event(self,
        timestamp: datetime.datetime, 
        guild_id: int, 
        interaction_type: UserInteraction,
        from_user: int,
        to_user: int
    ):
        event = InteractionEvent(timestamp, guild_id, interaction_type, from_user, to_user)
        self.database.log_event(event)
        
    def create_timeout_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        member: int,
        duration: int
    ):
        event = TimeoutEvent(timestamp, guild_id, member, duration)
        self.database.log_event(event)
        
    def create_jail_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        jail_event_type: JailEventType,
        jailed_by: int,
        duration: int,
        jail_reference: int
    ):
        event = JailEvent(timestamp, guild_id, jail_event_type, jailed_by, duration, jail_reference)
        self.database.log_event(event)