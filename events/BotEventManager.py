
import datetime
from discord.ext import commands
from BotLogger import BotLogger

from BotSettings import BotSettings
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from datalayer.UserRankings import UserRankings
from datalayer.UserStats import UserStats
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
    
    def get_user_statistics(self, user_id: int) -> UserStats:
        
        events = self.database.get_user_interaction_events(user_id)
        
        events_out = events["out"]
        events_in = events["in"]
        
        user_stats = UserStats()
        
        count_out = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0
        }
        user_count_out = {}
        
        for event in events_out:
            if event[Database.INTERACTION_EVENT_TYPE_COL] not in count_out.keys():
                continue
            
            count_out[event[Database.INTERACTION_EVENT_TYPE_COL]] += 1
            
            if event[Database.INTERACTION_EVENT_TO_COL] not in user_count_out.keys():
                user_count_out[event[Database.INTERACTION_EVENT_TO_COL]] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0
                }
            
            user_count_out[event[Database.INTERACTION_EVENT_TO_COL]][event[Database.INTERACTION_EVENT_TYPE_COL]] += 1
            
        user_stats.set_count_out(count_out)
        user_stats.set_user_count_out(user_count_out)
        
        count_in = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0
        }
        user_count_in = {}
        
        for event in events_in:
            count_in[event[Database.INTERACTION_EVENT_TYPE_COL]] += 1
            
            if event[Database.INTERACTION_EVENT_FROM_COL] not in user_count_in.keys():
                user_count_in[event[Database.INTERACTION_EVENT_FROM_COL]] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0
                }
            
            user_count_in[event[Database.INTERACTION_EVENT_FROM_COL]][event[Database.INTERACTION_EVENT_TYPE_COL]] += 1
        
        user_stats.set_count_in(count_in)
        user_stats.set_user_count_in(user_count_in)
        
        jail_events = self.database.get_user_jail_events(user_id)
        
        total_jail_duration = 0
        jail_stays = []
        total_added_to_self = 0
        total_reduced_from_self = 0
        
        for event in jail_events:
            
            duration = event[Database.JAIL_EVENT_DURATION_COL]
            
            if event[Database.JAIL_EVENT_TYPE_COL] in [JailEventType.FART, JailEventType.PET, JailEventType.SLAP]:
                if duration >= 0:
                    total_added_to_self += duration
                else:
                    total_reduced_from_self += duration
            
            total_jail_duration += duration
            jail_id = event[Database.JAIL_EVENT_JAILREFERENCE_COL]
            jail_stays.append(jail_id) if jail_id not in jail_stays else jail_stays

        user_stats.set_jail_total(total_jail_duration)
        user_stats.set_jail_amount(len(jail_stays))
        
        jail_interaction_events = self.database.get_user_jail_interaction_events(user_id)
        total_added_to_others = 0
        total_reduced_from_others = 0
        max_fart = None
        min_fart = None
        
        for event in jail_interaction_events:
            
            duration = event[Database.JAIL_EVENT_DURATION_COL]
            if event[Database.JAIL_EVENT_TYPE_COL] in [JailEventType.FART, JailEventType.PET, JailEventType.SLAP]:
                
                if duration >= 0:
                    total_added_to_others += duration
                else:
                    total_reduced_from_others += duration
                    
            if event[Database.JAIL_EVENT_TYPE_COL] == JailEventType.FART:  
                
                if max_fart is None or min_fart is None:
                    max_fart = duration
                    min_fart = duration
                    continue
                    
                max_fart = max(max_fart, duration)
                min_fart = min(min_fart, duration)

        user_stats.set_total_added_others(total_added_to_others)
        user_stats.set_total_added_self(total_added_to_self)
        user_stats.set_total_reduced_from_others(abs(total_reduced_from_others))
        user_stats.set_total_reduced_from_self(abs(total_reduced_from_self))
        user_stats.set_fart_stats(max_fart, min_fart)
        
        timeout_events = self.database.get_user_timeout_events(user_id)
        
        total_timeout_duration = 0
        timeout_count = len(timeout_events)
        
        for event in timeout_events:
            total_timeout_duration += event[Database.TIMEOUT_EVENT_DURATION_COL]
        
        user_stats.set_timeout_total(total_timeout_duration)
        user_stats.set_timeout_amount(timeout_count)
     
        
        return user_stats

    def get_user_rankings(self, guild_id: int):
        
        guild_interaction_events = self.database.get_guild_interaction_events(guild_id)
        
        user_rankings = UserRankings()
        
        slap_list = {}
        pet_list = {}
        fart_list = {}
        
        slap_reciever_list = {}
        pet_reciever_list = {}
        fart_reciever_list = {}
        
        for event in guild_interaction_events:
            
            match event[Database.INTERACTION_EVENT_TYPE_COL]:
                case UserInteraction.SLAP:
                    
                    if event[Database.INTERACTION_EVENT_FROM_COL] not in slap_list.keys():
                        slap_list[event[Database.INTERACTION_EVENT_FROM_COL]] = 1
                    else:
                        slap_list[event[Database.INTERACTION_EVENT_FROM_COL]] += 1
                    
                    if event[Database.INTERACTION_EVENT_TO_COL] not in slap_reciever_list.keys():
                        slap_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] = 1
                    else:
                        slap_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] += 1
                    
                case UserInteraction.PET:
                    
                    if event[Database.INTERACTION_EVENT_FROM_COL] not in pet_list.keys():
                        pet_list[event[Database.INTERACTION_EVENT_FROM_COL]] = 1
                    else:
                        pet_list[event[Database.INTERACTION_EVENT_FROM_COL]] += 1 
                    
                    if event[Database.INTERACTION_EVENT_TO_COL] not in pet_reciever_list.keys():
                        pet_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] = 1
                    else:
                        pet_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] += 1
                    
                case UserInteraction.FART:
                    
                    if event[Database.INTERACTION_EVENT_FROM_COL] not in fart_list.keys():
                        fart_list[event[Database.INTERACTION_EVENT_FROM_COL]] = 1
                    else:
                        fart_list[event[Database.INTERACTION_EVENT_FROM_COL]] += 1 
                    
                    if event[Database.INTERACTION_EVENT_TO_COL] not in fart_reciever_list.keys():
                        fart_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] = 1
                    else:
                        fart_reciever_list[event[Database.INTERACTION_EVENT_TO_COL]] += 1
        
        
        user_rankings.set_interaction_data(
            slap_list,
            pet_list,
            fart_list,
            slap_reciever_list,
            pet_reciever_list,
            fart_reciever_list
        )
        
        guild_timeout_events = self.database.get_guild_timeout_events(guild_id)
        
        timeout_lengths = {}
        timeout_count = {}
        
        for event in guild_timeout_events:
            
            if event[Database.TIMEOUT_EVENT_MEMBER_COL] not in timeout_lengths.keys():
                timeout_lengths[event[Database.TIMEOUT_EVENT_MEMBER_COL]] = event[Database.TIMEOUT_EVENT_DURATION_COL]
            else:
                timeout_lengths[event[Database.TIMEOUT_EVENT_MEMBER_COL]] += event[Database.TIMEOUT_EVENT_DURATION_COL]
            
            if event[Database.TIMEOUT_EVENT_MEMBER_COL] not in timeout_count.keys():
                timeout_count[event[Database.TIMEOUT_EVENT_MEMBER_COL]] = 1
            else:
                timeout_count[event[Database.TIMEOUT_EVENT_MEMBER_COL]] += 1
            
        user_rankings.set_timeout_data(
            timeout_lengths,
            timeout_count
        )
        
        guild_jail_events = self.database.get_guild_jail_events(guild_id)
        
        jail_lengths = {}
        jail_count = {}
        
        for event in guild_jail_events:
            
            if event[Database.JAIL_MEMBER_COL] not in jail_lengths.keys():
                jail_lengths[event[Database.JAIL_MEMBER_COL]] = event[Database.JAIL_EVENT_DURATION_COL]
            else:
                jail_lengths[event[Database.JAIL_MEMBER_COL]] += event[Database.JAIL_EVENT_DURATION_COL]
            
            if event[Database.JAIL_EVENT_TYPE_COL] == JailEventType.JAIL:
            
                if event[Database.JAIL_MEMBER_COL] not in jail_count.keys():
                    jail_count[event[Database.JAIL_MEMBER_COL]] = 1
                else:
                    jail_count[event[Database.JAIL_MEMBER_COL]] += 1
        
        user_rankings.set_jail_data(
            jail_lengths,
            jail_count
        )
        
        return user_rankings