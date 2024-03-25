from typing import List
import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class JailSettingsModal(discord.ui.Modal, title='Jail Settings'):
    slap_time = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.JAIL_SLAP_TIME_KEY)
    pet_time = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.JAIL_PET_TIME_KEY)
    fart_min_time = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.JAIL_FART_TIME_MIN_KEY)
    fart_max_time = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.JAIL_FART_TIME_MAX_KEY)
    base_crit_rate = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.JAIL_BASE_CRIT_RATE_KEY)

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'degenjail setup'

        self.slap_time.label = self.settings.get_setting_title(BotSettings.JAIL_SUBSETTINGS_KEY, BotSettings.JAIL_SLAP_TIME_KEY)
        self.pet_time.label = self.settings.get_setting_title(BotSettings.JAIL_SUBSETTINGS_KEY, BotSettings.JAIL_PET_TIME_KEY)
        self.fart_min_time.label = self.settings.get_setting_title(BotSettings.JAIL_SUBSETTINGS_KEY, BotSettings.JAIL_FART_TIME_MIN_KEY)
        self.fart_max_time.label = self.settings.get_setting_title(BotSettings.JAIL_SUBSETTINGS_KEY, BotSettings.JAIL_FART_TIME_MAX_KEY)
        self.base_crit_rate.label = self.settings.get_setting_title(BotSettings.JAIL_SUBSETTINGS_KEY, BotSettings.JAIL_BASE_CRIT_RATE_KEY)
    
    async def on_submit(self, interaction: discord.Interaction):
        text_inputs = [
            self.slap_time,
            self.pet_time,
            self.fart_min_time,
            self.fart_max_time,
            self.base_crit_rate
        ]
        errors: List[discord.ui.TextInput] = []
        
        for text_input in text_inputs:
            if not text_input.value.lstrip('-').isdigit() and text_input.custom_id != BotSettings.JAIL_BASE_CRIT_RATE_KEY:
                errors.append(text_input)
            elif text_input.custom_id == BotSettings.JAIL_BASE_CRIT_RATE_KEY:
                try:
                    if not (float(text_input.value) <= 1 and float(text_input.value) > 0):
                        errors.append(text_input)
                except ValueError:
                    errors.append(text_input)
                
                
        if len(errors) != 0:
            message = f'Illegal values:\n{', \n'.join([f'{text_input.label}({text_input.value})' for text_input in errors])}'
            await self.bot.response('Jail', interaction, message, self.command, args=[input.label for input in text_inputs])
            return
        
        if self.fart_min_time.value > self.fart_max_time.value :
            await self.bot.response('Jail', interaction, f'Fart minimum must be smaller than Fart maximum.', self.command, args=[input.label for input in text_inputs])
            return
            
        self.settings.set_jail_slap_time(interaction.guild_id, int(self.slap_time.value))
        self.settings.set_jail_pet_time(interaction.guild_id, int(self.pet_time.value))
        self.settings.set_jail_fart_min(interaction.guild_id, int(self.fart_min_time.value))
        self.settings.set_jail_fart_max(interaction.guild_id, int(self.fart_max_time.value))
        self.settings.set_jail_base_crit_rate(interaction.guild_id, float(self.base_crit_rate.value))
        
        await self.bot.response('Jail', interaction, f'Settings were successfully updated.', self.command, args=[input.label for input in text_inputs])