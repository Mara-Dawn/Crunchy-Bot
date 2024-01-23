
import datetime
import random
from typing import List, Tuple

import discord
from BotSettings import BotSettings

from BotUtil import BotUtil
from datalayer.UserInteraction import UserInteraction

class JailListNode():
    
    def __init__(self, user_id: int, timestamp: datetime.datetime, duration: int):
        
        self.user_id = user_id
        self.timestamp = timestamp
        self.duration = duration
        self.release_timestamp = timestamp + datetime.timedelta(minutes=duration) 
        self.jail_id: int = None
        
        self.slappers: List[int] = []
        self.petters: List[int] = []
        self.farters: List[int] = []

    
    def gt_user_id(self) -> int:
        
        return self.user_id
    
    def get_duration(self) -> int:
        
        return self.duration
    
    def get_duration_str(self) -> int:
        
        return BotUtil.strfdelta(self.duration, inputtype="minutes")
    
    def add_slapper(self, user_id: int) -> None:
        
        if user_id not in self.slappers:
            self.slappers.append(user_id)
            
    def add_petter(self, user_id: int) -> None:
        
        if user_id not in self.petters:
            self.petters.append(user_id)
            
    def add_farter(self, user_id: int) -> None:
        
        if user_id not in self.farters:
            self.farters.append(user_id)
            
    def get_slappers(self) -> List[int]:
        
        return self.slappers

    def get_petters(self) -> List[int]:
        
        return self.petters
    
    def get_farters(self) -> List[int]:
        
        return self.farters
    
    def set_jail_id(self, id: int):
        
        self.jail_id = id
        
    def get_jail_id(self) -> int:
        
        return self.jail_id
    
    def add_to_duration(self, amount: int) -> None:
        
        self.duration += amount
        self.release_timestamp = self.timestamp + datetime.timedelta(minutes=self.duration) 
    
    def get_timestamp(self) -> datetime.datetime:
        
        return self.timestamp
    
    def get_release_timestamp(self) -> datetime.datetime:
        
        return self.release_timestamp
    
    def get_remaining(self) -> float:
        
        remainder = self.release_timestamp - datetime.datetime.now()
        return remainder.total_seconds()
    
    def get_remaining_str(self) -> float:
        
        remainder = self.release_timestamp - datetime.datetime.now()
        
        return BotUtil.strfdelta(remainder)
    
    def get_list(self, type: UserInteraction) -> List[int]:
        
        match type:
            case UserInteraction.SLAP:
                return self.slappers
            case UserInteraction.PET:
                return self.petters
            case UserInteraction.FART:
                return self.farters
    
    def apply_interaction(self, type: UserInteraction, interaction: discord.Interaction, user: discord.Member, settings: BotSettings) -> Tuple[str, int]:
        
        response = ""
        amount = 0
        
        match type:
            case UserInteraction.SLAP:
                amount = settings.get_jail_slap_time(interaction.guild_id)
                self.add_to_duration(amount)
                self.add_slapper(interaction.user.id)
            case UserInteraction.PET:
                amount = -settings.get_jail_pet_time(interaction.guild_id)
                self.add_to_duration(amount)
                self.add_petter(interaction.user.id)
            case UserInteraction.FART:
                min_amount = settings.get_jail_fart_min(interaction.guild_id)
                max_amount = settings.get_jail_fart_max(interaction.guild_id)
                amount = random.randint(min_amount, max_amount)
                self.add_to_duration(amount)
                self.add_farter(interaction.user.id)
        
        if amount > 0:
            response += f'Their jail sentence was increased by {amount} minutes. '
        elif amount < 0: 
            response += f'Their jail sentence was reduced by {abs(amount)} minutes. '
            
        response += f'{self.get_remaining_str()} still remain.'
        
        return (response, amount)
            
        