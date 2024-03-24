import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class BeansDailySettingsModal(discord.ui.Modal, title='Beans Settings'):

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'beans daily setup'
        
    beans_daily_min = discord.ui.TextInput(
        label='Daily Beans Minimum',
        required=False,
    )
    
    beans_daily_max = discord.ui.TextInput(
        label='Daily Beans Maximum',
        required=False,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        values = {
            'Beans minimum': self.beans_daily_min.value,
            'Beans maximum': self.beans_daily_max.value
        }
        error = {}
        
        for key, value in values.items():
            if not value.lstrip('-').isdigit():
                error[key] = value
                
        if len(error) != 0:
            message = f'Illegal values: {', '.join([f'{key}({value})' for key, value in error.items()])}'
            await self.bot.response('Beans', interaction, message, self.command, args=values.values())
            return
        
        if values['Beans minimum'] > values['Beans maximum'] :
            await self.bot.response('Beans', interaction, f'Beans minimum must be smaller than Beans maximum.', self.command, args=values.values())
            return
            
        self.settings.set_beans_daily_min(interaction.guild_id, int(values['Beans minimum']))
        self.settings.set_beans_daily_max(interaction.guild_id, int(values['Beans maximum']))
        
        await self.bot.response('Beans', interaction, f'Settings were successfully updated.', self.command, args=values.values())