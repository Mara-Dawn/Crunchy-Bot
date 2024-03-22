import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class JailSettingsModal(discord.ui.Modal, title='Jail Settings'):

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'degenjail setup'
        
    slap_time = discord.ui.TextInput(
        label='Slap Time (added)',
        required=False,
    )
    
    pet_time = discord.ui.TextInput(
        label='Pet Time (subtracted)',
        required=False,
    )
    
    fart_min_time = discord.ui.TextInput(
        label='Fart minimum',
        required=False,
    )
    
    fart_max_time = discord.ui.TextInput(
        label='Fart maximum',
        required=False,
    )
    
    base_crit_rate = discord.ui.TextInput(
        label='Base Crit Rate',
        required=False,
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        values = {
            'Slap time': self.slap_time.value,
            'Pet time': self.pet_time.value,
            'Fart minimum': self.fart_min_time.value,
            'Fart maximum': self.fart_max_time.value,
            'Base Crit Rate': self.base_crit_rate.value
        }
        error = {}
        
        for key, value in values.items():
            if not value.lstrip('-').isdigit() and key != 'Base Crit Rate':
                error[key] = value
            elif key == 'Base Crit Rate' and value.lstrip('-').isdecimal() and float(value) <= 1 and float(value) > 0:
                error[key] = value
                
        
        if len(error) != 0:
            message = f'Illegal values: {', '.join([f'{key}({value})' for key, value in error.items()])}'
            await self.bot.response('Jail', interaction, message, self.command, *values.values())
            return
        
        if values['Fart minimum'] > values['Fart maximum'] :
            await self.bot.response('Jail', interaction, f'Fart minimum must be smaller than Fart maximum.', self.command, *values.values())
            return
            
        self.settings.set_jail_slap_time(interaction.guild_id, int(values['Slap time']))
        self.settings.set_jail_pet_time(interaction.guild_id, int(values['Pet time']))
        self.settings.set_jail_fart_min(interaction.guild_id, int(values['Fart minimum']))
        self.settings.set_jail_fart_max(interaction.guild_id, int(values['Fart maximum']))
        self.settings.set_jail_base_crit_rate(interaction.guild_id, float(values['Base Crit Rate']))
        
        await self.bot.response('Jail', interaction, f'Settings were successfully updated.', self.command, *values.values())