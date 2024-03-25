from typing import List
import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class PoliceSettingsModal(discord.ui.Modal, title='Police Settings'):
    timeout_length = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.POLICE_TIMEOUT_LENGTH_KEY)
    message_limit = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.POLICE_MESSAGE_LIMIT_KEY)
    message_limit_interval = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.POLICE_MESSAGE_LIMIT_INTERVAL_KEY)
    timeouts_before_jail = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.POLICE_TIMEOUTS_BEFORE_JAIL_KEY)
    timeout_jail_duration = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.POLICE_TIMEOUT_JAIL_DURATION_KEY)

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'police setup'

        self.timeout_length.label = self.settings.get_setting_title(BotSettings.POLICE_SUBSETTINGS_KEY, BotSettings.POLICE_TIMEOUT_LENGTH_KEY)
        self.message_limit.label = self.settings.get_setting_title(BotSettings.POLICE_SUBSETTINGS_KEY, BotSettings.POLICE_MESSAGE_LIMIT_KEY)
        self.message_limit_interval.label = self.settings.get_setting_title(BotSettings.POLICE_SUBSETTINGS_KEY, BotSettings.POLICE_MESSAGE_LIMIT_INTERVAL_KEY)
        self.timeouts_before_jail.label = self.settings.get_setting_title(BotSettings.POLICE_SUBSETTINGS_KEY, BotSettings.POLICE_TIMEOUTS_BEFORE_JAIL_KEY)
        self.timeout_jail_duration.label = self.settings.get_setting_title(BotSettings.POLICE_SUBSETTINGS_KEY, BotSettings.POLICE_TIMEOUT_JAIL_DURATION_KEY)
    
    async def on_submit(self, interaction: discord.Interaction):
        text_inputs = [ 
            self.timeout_length,
            self.message_limit,
            self.message_limit_interval,
            self.timeouts_before_jail,
            self.timeout_jail_duration,
        ]
        errors: List[discord.ui.TextInput] = []
        
        for text_input in text_inputs:
            if not text_input.value.isdigit():
                errors.append(text_input)
        
        if len(errors) != 0:
            message = f'Illegal values:\n{', \n'.join([f'{text_input.label}({text_input.value})' for text_input in errors])}\nPlease only use positive integers.'
            await self.bot.response('Police', interaction, message, self.command, args=[text_input.label for text_input in text_inputs])
            return
        
        self.settings.set_police_timeout(interaction.guild_id, int(self.timeout_length.value))
        self.settings.set_police_message_limit(interaction.guild_id, int(self.message_limit.value))
        self.settings.set_police_message_limit_interval(interaction.guild_id, int(self.message_limit_interval.value))
        self.settings.set_police_timeouts_before_jail(interaction.guild_id, int(self.timeouts_before_jail.value))
        self.settings.set_police_timeout_jail_duration(interaction.guild_id, int(self.timeout_jail_duration.value))
        
        await self.bot.response('Police', interaction, f'Settings were successfully updated.', self.command, args=[text_input.label for text_input in text_inputs])