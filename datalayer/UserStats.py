from typing import Dict
from datalayer.UserInteraction import UserInteraction


class UserStats():
    
    def __init__(self):
        self.count_in = {}
        self.count_out = {}
        self.user_count_in = {}
        self.user_count_out = {}
        self.jail_total_duration = 0
        self.jail_count = 0
        self.timeout_total_duration = 0
        self.timeout_count = 0
        self.min_fart = 0
        self.max_fart = 0
        self.total_added_to_others = 0
        self.total_added_to_self = 0
              
    def set_count_in(self, count_in: Dict[UserInteraction, int]):
        self.count_in = count_in
          
    def set_count_out(self, count_out: Dict[UserInteraction, int]):
        self.count_out = count_out
   
    def set_user_count_in(self, user_count_in: Dict[str, int]):
        self.user_count_in = user_count_in
        
    def set_user_count_out(self, user_count_out: Dict[str, int]):
        self.user_count_out = user_count_out
        
    def set_jail_total(self, duration: int):
        self.jail_total_duration = duration
        
    def set_jail_amount(self, amount: int):
        self.jail_count = amount
     
    def set_timeout_total(self, duration: int):
        self.timeout_total_duration = duration
        
    def set_timeout_amount(self, amount: int):
        self.timeout_count = amount
    
    def set_fart_stats(self, max_fart: int, min_fart: int):
        self.min_fart = min_fart
        self.max_fart = max_fart
        
    def set_total_added_others(self, total_added_to_others: int):
        self.total_added_to_others = total_added_to_others
        
    def set_total_added_self(self, total_added_to_self: int):
        self.total_added_to_self = total_added_to_self
        
    def get_slaps_recieved(self):
        return self.count_in[UserInteraction.SLAP]
    
    def get_slaps_given(self):
        return self.count_out[UserInteraction.SLAP]
    
    def get_pets_recieved(self):
        return self.count_in[UserInteraction.PET]
    
    def get_pets_given(self):
        return self.count_out[UserInteraction.PET]
    
    def get_farts_recieved(self):
        return self.count_in[UserInteraction.FART]
    
    def get_farts_given(self):
        return self.count_out[UserInteraction.FART]
    
    def __get_top(self, type: UserInteraction, amount: int, data):
        if len(data) == 0:
            return {}
        
        lst = {k: v[type] for (k, v) in data.items()}
        lst_filtered = {}
        for (k, v) in lst.items():
            if v > 0:
                lst_filtered[k] = v
        lst_sorted = sorted(lst_filtered.items(), key=lambda item: item[1], reverse=True)
        if len(lst_sorted) == 1:
            return lst_sorted
        
        amount = min(amount, len(data))
        return lst_sorted[:amount]
    
    def get_top_slappers(self, amount: int):
        return self.__get_top(UserInteraction.SLAP, amount, self.user_count_in)
    
    def get_top_petters(self, amount: int):
        return self.__get_top(UserInteraction.PET, amount, self.user_count_in)
    
    def get_top_farters(self, amount: int):
        return self.__get_top(UserInteraction.FART, amount, self.user_count_in)
    
    def get_top_slapperd(self, amount: int):
        return self.__get_top(UserInteraction.SLAP, amount, self.user_count_out)
    
    def get_top_petterd(self, amount: int):
        return self.__get_top(UserInteraction.PET, amount, self.user_count_out)
    
    def get_top_farterd(self, amount: int):
        return self.__get_top(UserInteraction.FART, amount, self.user_count_out)
    
    def get_jail_count(self):
        return self.jail_count
        
    def get_jail_total(self):
        return self.jail_total_duration
        
    def get_timeout_count(self):
        return self.timeout_count
        
    def get_timeout_total(self):
        return self.timeout_total_duration

    def get_biggest_fart(self):
        return self.max_fart
    
    def get_smallest_fart(self):
        return self.min_fart
    
    def get_total_added_others(self):
        return self.total_added_to_others
        
    def get_total_added_self(self):
        return self.total_added_to_self