from typing import Dict
from BotUtil import BotUtil
from datalayer.UserInteraction import UserInteraction
from view.RankingType import RankingType

class UserRankings():
    
    def __init__(self):
        
        self.slap_list = {}
        self.pet_list = {}
        self.fart_list = {}
        
        self.slap_reciever_list = {}
        self.pet_reciever_list = {}
        self.fart_reciever_list = {}
        
        self.timeout_lengths = {}
        self.timeout_count = {}
        
        self.jail_lengths = {}
        self.jail_count = {}
    
    def set_interaction_data(self, slap_list, pet_list, fart_list, slap_reciever_list, pet_reciever_list, fart_reciever_list):
        self.slap_list = slap_list
        self.pet_list = pet_list
        self.fart_list = fart_list
        
        self.slap_reciever_list = slap_reciever_list
        self.pet_reciever_list = pet_reciever_list
        self.fart_reciever_list = fart_reciever_list
        
    def set_timeout_data(self, timeout_lengths, timeout_count):
        self.timeout_lengths = timeout_lengths
        self.timeout_count = timeout_count
        
    def set_jail_data(self, jail_lengths, jail_count):
        self.jail_lengths = jail_lengths
        self.jail_count = jail_count
    
    
    def get_rankings(self, type: RankingType):
        
        
        def convert(list):
            new_list = []
            for (k,v) in list:
                new_list.append((k, BotUtil.strfdelta(sorted_list, inputtype='seconds')))
            return new_list
                
        match type:
            case RankingType.SLAP: 
                return sorted(self.slap_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.PET:
                return sorted(self.pet_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.FART:
                return sorted(self.fart_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.SLAP_RECIEVED:
                return sorted(self.slap_reciever_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.PET_RECIEVED:
                return sorted(self.pet_reciever_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.FART_RECIEVED:
                return sorted(self.fart_reciever_list.items(), key=lambda item: item[1], reverse=True)
            case RankingType.TIMEOUT_TOTAL:
                sorted_list = sorted(self.timeout_lengths.items(), key=lambda item: item[1], reverse=True)
                converted = [(k, BotUtil.strfdelta(v, inputtype='seconds')) for (k,v) in sorted_list]
                return converted
            case RankingType.TIMEOUT_COUNT:
                return sorted(self.timeout_count.items(), key=lambda item: item[1], reverse=True)
            case RankingType.JAIL_TOTAL:
                sorted_list =  sorted(self.jail_lengths.items(), key=lambda item: item[1], reverse=True)
                converted = [(k, BotUtil.strfdelta(v, inputtype='minutes')) for (k,v) in sorted_list]
                return converted
            case RankingType.JAIL_COUNT:
                return sorted(self.jail_count.items(), key=lambda item: item[1], reverse=True)