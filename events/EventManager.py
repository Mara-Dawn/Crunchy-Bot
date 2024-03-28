import datetime

from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from datalayer.UserJail import UserJail
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from datalayer.UserRankings import UserRankings
from datalayer.UserStats import UserStats
from events.BeansEvent import BeansEvent
from events.BeansEventType import BeansEventType
from events.InteractionEvent import InteractionEvent
from events.InventoryEvent import InventoryEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.SpamEvent import SpamEvent
from events.TimeoutEvent import TimeoutEvent
from events.QuoteEvent import QuoteEvent
from shop.ItemType import ItemType

class EventManager():

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
    
    def dispatch_spam_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        member: int
    ):
        event = SpamEvent(timestamp, guild_id, member)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Spam event was logged.', self.log_name)
    
    def dispatch_jail_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        jail_event_type: JailEventType,
        caused_by: int,
        duration: int,
        jail_reference: int
    ):
        event = JailEvent(timestamp, guild_id, jail_event_type, caused_by, duration, jail_reference)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Jail event `{jail_event_type}` was logged for jail {jail_reference}.', self.log_name)
        
        if jail_event_type is JailEventType.RELEASE:
            self.database.log_jail_release(jail_reference, int(timestamp.timestamp()))
            self.logger.log(guild_id, f'Jail sentence `{jail_reference}` marked as released.', self.log_name)
    
    def dispatch_quote_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        quote_id: int
    ):
        event = QuoteEvent(timestamp, guild_id, quote_id)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Quote event was logged.', self.log_name)
        
    def dispatch_beans_event(self,
        timestamp: datetime.datetime, 
        guild_id: int,
        beans_event_type: BeansEventType,
        member: int,
        value: int,
    ) -> int:
        event = BeansEvent(timestamp, guild_id, beans_event_type, member, value)
        id = self.database.log_event(event)
        self.logger.log(guild_id, f'Beans event `{beans_event_type}` was logged. [{value}]', self.log_name)
        return id
    
    def dispatch_inventory_event(self,
        timestamp: datetime.datetime, 
        guild_id: int,
        member_id: int,
        item_type: ItemType,
        beans_event_id: int,
        amount: int,
    ):
        event = InventoryEvent(timestamp, guild_id, member_id, item_type, beans_event_id, amount)
        self.database.log_event(event)
        self.logger.log(guild_id, f'Inventory event for {amount} `{item_type}` was logged.', self.log_name)
    
    def get_jail_duration(self, jail: UserJail) -> int:
        events = self.database.get_jail_events_by_jail(jail.get_id())
        total_duration = 0
        for event in events:
            total_duration += event.get_duration()
        
        return total_duration
    
    def get_jail_remaining(self, jail: UserJail) -> float:
        duration = self.get_jail_duration(jail)
        release_timestamp = jail.get_jailed_on() + datetime.timedelta(minutes=duration) 
        remainder = release_timestamp - datetime.datetime.now()
        return max(remainder.total_seconds()/60, 0)
    
    def has_jail_event_from_user(self, jail_id: int, user_id: int, type: JailEventType) -> bool:
        events = self.database.get_jail_events_by_user(user_id)
        
        for event  in events:
            if event.get_jail_id() == jail_id and event.get_jail_event_type() == type:
                return True
        
        return False
    
    def get_user_statistics(self, user_id: int) -> UserStats:
        events_out = self.database.get_interaction_events_by_user(user_id)
        
        user_stats = UserStats()
        
        count_out = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0
        }
        user_count_out = {}
        
        for event in events_out:
            interaction_type = event.get_interaction_type()
            
            if interaction_type not in count_out.keys():
                continue
            
            count_out[interaction_type] += 1
            member_id = event.get_to_user()
            if member_id not in user_count_out.keys():
                user_count_out[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0
                }
            
            user_count_out[member_id][interaction_type] += 1
            
        user_stats.set_count_out(count_out)
        user_stats.set_user_count_out(user_count_out)
        
        events_in = self.database.get_interaction_events_affecting_user(user_id)
        
        count_in = {
            UserInteraction.SLAP: 0,
            UserInteraction.PET: 0,
            UserInteraction.FART: 0
        }
        user_count_in = {}
        
        for event in events_in:
            interaction_type = event.get_interaction_type()
            
            count_in[interaction_type] += 1
            member_id = event.get_from_user()
            if member_id not in user_count_in.keys():
                user_count_in[member_id] = {
                    UserInteraction.SLAP: 0,
                    UserInteraction.PET: 0,
                    UserInteraction.FART: 0
                }
            
            user_count_in[member_id][interaction_type] += 1
        
        user_stats.set_count_in(count_in)
        user_stats.set_user_count_in(user_count_in)
        
        jail_events = self.database.get_jail_events_affecting_user(user_id)
        
        total_jail_duration = 0
        jail_stays = []
        total_added_to_self = 0
        total_reduced_from_self = 0
        
        for event in jail_events:
            duration = event.get_duration()
            if event.get_jail_event_type() in [JailEventType.FART, JailEventType.PET, JailEventType.SLAP]:
                if duration >= 0:
                    total_added_to_self += duration
                else:
                    total_reduced_from_self += duration
            
            total_jail_duration += duration
            jail_id = event.get_jail_id()
            jail_stays.append(jail_id) if jail_id not in jail_stays else jail_stays

        user_stats.set_jail_total(total_jail_duration)
        user_stats.set_jail_amount(len(jail_stays))
        
        jail_interaction_events = self.database.get_jail_events_by_user(user_id)
        total_added_to_others = 0
        total_reduced_from_others = 0
        max_fart = None
        min_fart = None
        
        for event in jail_interaction_events:
            duration = event.get_duration()
            if event.get_jail_event_type() in [JailEventType.FART, JailEventType.PET, JailEventType.SLAP]:
                
                if duration >= 0:
                    total_added_to_others += duration
                else:
                    total_reduced_from_others += duration
                    
            if event.get_jail_event_type() == JailEventType.FART:  
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
        
        timeout_events = self.database.get_timeout_events_by_user(user_id)
        
        total_timeout_duration = 0
        timeout_count = len(timeout_events)
        
        for event in timeout_events:
            total_timeout_duration += event.get_duration()
        
        user_stats.set_timeout_total(total_timeout_duration)
        user_stats.set_timeout_amount(timeout_count)
        
        spam_events = self.database.get_spam_events_by_user(user_id)
        spam_count = len(spam_events)
        user_stats.set_spam_score(spam_count)
     
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
            from_user_id = event.get_from_user()
            to_user_id = event.get_to_user()
            
            match event.get_interaction_type():
                case UserInteraction.SLAP:
                    BotUtil.dict_append(slap_list, from_user_id, 1)
                    BotUtil.dict_append(slap_reciever_list, to_user_id, 1)
                case UserInteraction.PET:
                    BotUtil.dict_append(pet_list, from_user_id, 1)
                    BotUtil.dict_append(pet_reciever_list, to_user_id, 1)
                case UserInteraction.FART:
                    BotUtil.dict_append(fart_list, from_user_id, 1)
                    BotUtil.dict_append(fart_reciever_list, to_user_id, 1)
        
        user_rankings.set_interaction_data(
            slap_list,
            pet_list,
            fart_list,
            slap_reciever_list,
            pet_reciever_list,
            fart_reciever_list
        )
        
        guild_timeout_events = self.database.get_timeout_events_by_guild(guild_id)
        
        timeout_lengths = {}
        timeout_count = {}
        
        for event in guild_timeout_events:
            member_id = event.get_member()
            
            BotUtil.dict_append(timeout_lengths, member_id, event.get_duration())
            BotUtil.dict_append(timeout_count, member_id, 1)
            
        user_rankings.set_timeout_data(
            timeout_lengths,
            timeout_count
        )
        
        jail_data = self.database.get_jail_events_by_guild(guild_id)
        
        jail_lengths = {}
        jail_count = {}
        
        for jail, events in jail_data.items():
            for event in events:
                jail_member = jail.get_member_id()
                BotUtil.dict_append(jail_lengths, jail_member, event.get_duration())
                
                if event.get_jail_event_type() == JailEventType.JAIL:
                    BotUtil.dict_append(jail_count, jail_member, 1)
        
        user_rankings.set_jail_data(
            jail_lengths,
            jail_count
        )
        
        guild_spam_events = self.database.get_spam_events_by_guild(guild_id)
        
        spam_count = {}
        
        for event in guild_spam_events:
            member_id = event.get_member()
            BotUtil.dict_append(spam_count, member_id, 1)
            
        user_rankings.set_spam_data(spam_count)

        guild_beans_balances = self.database.get_guild_beans_gained(guild_id)

        user_rankings.set_beans_data(guild_beans_balances)
        
        return user_rankings