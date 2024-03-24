import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class BeansGambaSettingsModal(discord.ui.Modal, title='Beans Settings'):

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'beans gamba setup'
    
    beans_gamba_cost = discord.ui.TextInput(
        label='Beans Gamba Cost',
        required=False,
    )
    
    beans_gamba_cooldown = discord.ui.TextInput(
        label='Beans Gamba Cooldown',
        required=False,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        values = {
            'Beans Gamba Cost': self.beans_gamba_cost.value,
            'Beans Gamba Cooldown': self.beans_gamba_cooldown.value
        }
        error = {}
        
        for key, value in values.items():
            if not value.lstrip('-').isdigit():
                error[key] = value
                
        if len(error) != 0:
            message = f'Illegal values: {', '.join([f'{key}({value})' for key, value in error.items()])}'
            await self.bot.response('Beans', interaction, message, self.command, args=values.values())
            return
            
        self.settings.set_beans_gamba_cost(interaction.guild_id, int(values['Beans Gamba Cost']))
        self.settings.set_beans_gamba_cooldown(interaction.guild_id, int(values['Beans Gamba Cooldown']))
        
        await self.bot.response('Beans', interaction, f'Settings were successfully updated.', self.command, args=values.values())