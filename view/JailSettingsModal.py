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
    
    async def on_submit(self, interaction: discord.Interaction):
        values = {
            'Slap time': self.slap_time.value,
            'Pet time': self.pet_time.value,
            'Fart minimum': self.fart_min_time.value,
            'Fart maximum': self.fart_max_time.value
        }
        error = {}
        
        for key, value in values.items():
            if not value.lstrip('-').isdigit():
                error[key] = value
        
        if len(error) != 0:
            message = f'Illegal values: {', '.join([f'{key}({value})' for key, value in error.items()])}\nPlease only use integers.'
            await self.bot.response('Jail', interaction, message, self.command, *values.values())
            return
        
        values = {key: int(value) for (key, value) in values.items()}
        
        if values['Fart minimum'] > values['Fart maximum'] :
            await self.bot.response('Jail', interaction, f'Fart minimum must be smaller than Fart maximum.', self.command, *values.values())
            return
            
        self.settings.set_jail_slap_time(interaction.guild_id, values['Slap time'])
        self.settings.set_jail_pet_time(interaction.guild_id, values['Pet time'])
        self.settings.set_jail_fart_min(interaction.guild_id, values['Fart minimum'])
        self.settings.set_jail_fart_max(interaction.guild_id, values['Fart maximum'])
        
        await self.bot.response('Jail', interaction, f'Settings were successfully updated.', self.command, *values.values())