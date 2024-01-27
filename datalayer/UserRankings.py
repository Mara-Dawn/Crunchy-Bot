from typing import Dict, List, Tuple
from BotUtil import BotUtil
from view.RankingType import RankingType

class UserRankings():
    
    def __init__(self):
        self.slap_list: Dict[int, int] = {}
        self.pet_list: Dict[int, int] = {}
        self.fart_list: Dict[int, int] = {}
        
        self.slap_reciever_list: Dict[int, int] = {}
        self.pet_reciever_list: Dict[int, int] = {}
        self.fart_reciever_list: Dict[int, int] = {}
        
        self.timeout_lengths: Dict[int, int] = {}
        self.timeout_count: Dict[int, int] = {}
        
        self.jail_lengths: Dict[int, int] = {}
        self.jail_count: Dict[int, int] = {}
    
    def set_interaction_data(
        self, 
        slap_list: Dict[int, int], 
        pet_list: Dict[int, int], 
        fart_list: Dict[int, int], 
        slap_reciever_list: Dict[int, int], 
        pet_reciever_list: Dict[int, int], 
        fart_reciever_list: Dict[int, int]
    ):
        self.slap_list = slap_list
        self.pet_list = pet_list
        self.fart_list = fart_list
        
        self.slap_reciever_list = slap_reciever_list
        self.pet_reciever_list = pet_reciever_list
        self.fart_reciever_list = fart_reciever_list
        
    def set_timeout_data(self, timeout_lengths: Dict[int, int], timeout_count: Dict[int, int]):
        self.timeout_lengths = timeout_lengths
        self.timeout_count = timeout_count
        
    def set_jail_data(self, jail_lengths: Dict[int, int], jail_count: Dict[int, int]):
        self.jail_lengths = jail_lengths
        self.jail_count = jail_count
    
    
    def get_rankings(self, type: RankingType) -> List[Tuple]:
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