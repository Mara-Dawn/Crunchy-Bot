import datetime
from typing import Any, List, Tuple

from discord.ext import commands
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from datalayer.Quote import Quote
from datalayer.UserJail import UserJail
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from datalayer.UserStats import UserStats
from events.BeansEvent import BeansEvent
from events.BeansEventType import BeansEventType
from events.BotEvent import BotEvent
from events.InteractionEvent import InteractionEvent
from events.InventoryEvent import InventoryEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.LootBoxEvent import LootBoxEvent
from events.LootBoxEventType import LootBoxEventType
from events.SpamEvent import SpamEvent
from events.TimeoutEvent import TimeoutEvent
from events.QuoteEvent import QuoteEvent
from shop.ItemType import ItemType
from view.RankingType import RankingType

class EventManager():

    def __init__(self, bot: commands.Bot, settings: BotSettings, database: Database, logger: BotLogger):
        self.bot = bot
        self.settings = settings
        self.database = database
        self.logger = logger
        self.log_name = "Events"
    
    def __log_event(self, event: BotEvent, member_id: int, *args):
        type = event.get_type()
        guild_id = event.get_guild_id()
        arguments = ', '.join([str(x) for x in args])
        self.logger.log(guild_id, f'{type.value} event was logged for {BotUtil.get_name(self.bot, guild_id, member_id, 30)}. Arguments: {arguments}', self.log_name)
    
    def dispatch_interaction_event(self,
        timestamp: datetime.datetime, 
        guild_id: int, 
        interaction_type: UserInteraction,
        from_user: int,
        to_user: int
    ):
        event = InteractionEvent(timestamp, guild_id, interaction_type, from_user, to_user)
        self.database.log_event(event)
        self.__log_event(event, from_user, BotUtil.get_name(self.bot, guild_id, to_user, 30))
        
    def dispatch_timeout_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        member: int,
        duration: int
    ):
        event = TimeoutEvent(timestamp, guild_id, member, duration)
        self.database.log_event(event)
        self.__log_event(event, member, duration)
    
    def dispatch_spam_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        member: int
    ):
        event = SpamEvent(timestamp, guild_id, member)
        self.database.log_event(event)
        self.__log_event(event, member)
    
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
        self.__log_event(event, caused_by, jail_event_type, duration, jail_reference)
        
        if jail_event_type is JailEventType.RELEASE:
            self.database.log_jail_release(jail_reference, int(timestamp.timestamp()))
            self.logger.log(guild_id, f'Jail sentence `{jail_reference}` marked as released.', self.log_name)
    
    def dispatch_quote_event(self,
        timestamp: datetime.datetime,
        guild_id: int, 
        quote: Quote
    ):
        event = QuoteEvent(timestamp, guild_id, quote.get_id())
        self.database.log_event(event)
        self.__log_event(event, quote.get_saved_by(), quote.get_member_name(), quote.get_message_content())
        
    def dispatch_beans_event(self,
        timestamp: datetime.datetime, 
        guild_id: int,
        beans_event_type: BeansEventType,
        member: int,
        value: int,
    ) -> int:
        event = BeansEvent(timestamp, guild_id, beans_event_type, member, value)
        id = self.database.log_event(event)
        self.__log_event(event, member, beans_event_type, f'[{value}]')
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
        self.__log_event(event, member_id, item_type, amount)
        
    def dispatch_loot_box_event(self,
        timestamp: datetime.datetime, 
        guild_id: int,
        loot_box_id: int,
        member_id: int,
        loot_box_event_type: LootBoxEventType
    ):
        event = LootBoxEvent(timestamp, guild_id, loot_box_id, member_id, loot_box_event_type)
        self.database.log_event(event)
        self.__log_event(event, member_id, loot_box_event_type, loot_box_id)
    
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
    
    def __get_ranking_data_by_type(self, guild_id: int, outgoing: bool, interaction_type: UserInteraction) -> List[Tuple[int, Any]]:
        guild_interaction_events = self.database.get_guild_interaction_events(guild_id, interaction_type)
        parsing_list = {}
            
        for event in guild_interaction_events:
            user_id = event.get_to_user()
            if outgoing: # True = from, False = to
                user_id = event.get_from_user()

            BotUtil.dict_append(parsing_list, user_id, 1)

        return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)    
    
    def get_user_rankings(self, guild_id: int, ranking_type: RankingType) -> List[Tuple[int, Any]]:
        parsing_list = {}
        match ranking_type:
            case RankingType.SLAP:
                return self.__get_ranking_data_by_type(guild_id, outgoing = True, interaction_type = UserInteraction.SLAP)
            case RankingType.PET:
                return self.__get_ranking_data_by_type(guild_id, outgoing = True, interaction_type = UserInteraction.PET)
            case RankingType.FART:
                return self.__get_ranking_data_by_type(guild_id, outgoing = True, interaction_type = UserInteraction.FART)
            case RankingType.SLAP_RECIEVED:
                return self.__get_ranking_data_by_type(guild_id, outgoing = False, interaction_type = UserInteraction.SLAP)
            case RankingType.PET_RECIEVED:
                return self.__get_ranking_data_by_type(guild_id, outgoing = False, interaction_type = UserInteraction.PET)
            case RankingType.FART_RECIEVED:
                return self.__get_ranking_data_by_type(guild_id, outgoing = False, interaction_type = UserInteraction.FART)
            case RankingType.TIMEOUT_TOTAL:
                guild_timeout_events = self.database.get_timeout_events_by_guild(guild_id)
                for event in guild_timeout_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, event.get_duration())
                sorted_list = sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
                converted = [(k, BotUtil.strfdelta(v, inputtype='seconds')) for (k,v) in sorted_list]
                return converted
            case RankingType.TIMEOUT_COUNT:
                guild_timeout_events = self.database.get_timeout_events_by_guild(guild_id)
                for event in guild_timeout_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.JAIL_TOTAL:
                jail_data = self.database.get_jail_events_by_guild(guild_id)
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.get_member_id()
                        BotUtil.dict_append(parsing_list, user_id, event.get_duration())
                sorted_list =  sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
                converted = [(k, BotUtil.strfdelta(v, inputtype='minutes')) for (k,v) in sorted_list]
                return converted
            case RankingType.JAIL_COUNT:
                jail_data = self.database.get_jail_events_by_guild(guild_id)
                for jail, events in jail_data.items():
                    for event in events:
                        user_id = jail.get_member_id()
                        if event.get_jail_event_type() == JailEventType.JAIL:
                            BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.SPAM_SCORE:
                guild_spam_events = self.database.get_spam_events_by_guild(guild_id)
                for event in guild_spam_events:
                    user_id = event.get_member()
                    BotUtil.dict_append(parsing_list, user_id, 1)
                return sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.BEANS:
                parsing_list = self.database.get_guild_beans_rankings(guild_id)
                lootbox_purchases = self.database.get_lootbox_purchases_by_guild(guild_id)
                loot_box_item = self.bot.item_manager.get_item(guild_id, ItemType.LOOTBOX)
                for user_id, amount in lootbox_purchases.items():
                    if user_id in parsing_list.keys():
                        parsing_list[user_id] -= amount * loot_box_item.get_cost()
                sorted_list = sorted(parsing_list.items(), key=lambda item: item[1], reverse=True)
                converted = [(k, f'🅱️{v}') for (k,v) in sorted_list]
                return converted