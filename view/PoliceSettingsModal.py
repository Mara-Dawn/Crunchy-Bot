import discord
from BotSettings import BotSettings
from MaraBot import MaraBot

class PoliceSettingsModal(discord.ui.Modal, title='Police Settings'):

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'police setup'
        
    timeout_length = discord.ui.TextInput(
        label='Timeout Length (seconds)',
        required=False,
    )
    
    message_limit = discord.ui.TextInput(
        label='Message Limit (count)',
        required=False,
    )
    
    message_limit_interval = discord.ui.TextInput(
        label='Limit Interval (seconds)',
        required=False,
    )
    
    timeouts_before_jail = discord.ui.TextInput(
        label='Timeouts before jail (count)',
        required=False,
    )
    
    timeout_jail_duration = discord.ui.TextInput(
        label='Jail duration (minutes)',
        required=False,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        
        values = {
            'Timeout Length': self.timeout_length.value,
            'Message Limit': self.message_limit.value,
            'Limit Interval': self.message_limit_interval.value,
            'Timeouts before jail': self.timeouts_before_jail.value,
            'Jail duration': self.timeout_jail_duration.value,
        }
        error = {}
        
        for key, value in values.items():
            if not value.isdigit():
                error[key] = value
        
        if len(error) != 0:
            message = f'Illegal values: {', '.join([f'{key}({value})' for key, value in error.items()])}\nPlease only use positive integers.'
            await self.bot.response('Police', interaction, message, *values.values())
            return
        
        values = {key: int(value) for (key, value) in values.items()}
        
        self.settings.set_police_timeout(interaction.guild_id, values['Timeout Length'])
        self.settings.set_police_message_limit(interaction.guild_id, values['Message Limit'])
        self.settings.set_police_message_limit_interval(interaction.guild_id, values['Limit Interval'])
        self.settings.set_police_message_limit(interaction.guild_id, values['Message Limit'])
        self.settings.set_police_timeouts_before_jail(interaction.guild_id, values['Timeouts before jail'])
        self.settings.set_police_timeout_jail_duration(interaction.guild_id, values['Jail duration'])
        
        await self.bot.response('Police', interaction, f'Settings were successfully updated.', self.command, *values.values())