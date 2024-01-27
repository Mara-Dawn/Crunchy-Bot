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
    
    timeout_notice = discord.ui.TextInput(
        label='Timeout Warning Message',
        style=discord.TextStyle.long,
        required=False,
        max_length=300,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        timeout_notice = self.timeout_notice.value
        
        values = {
            'Timeout Length': self.timeout_length.value,
            'Message Limit': self.message_limit.value,
            'Limit Interval': self.message_limit_interval.value,
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
        self.settings.set_police_timeout_notice(interaction.guild_id, timeout_notice)
        
        await self.bot.response('Police', interaction, f'Settings were successfully updated.', self.command, *values.values())