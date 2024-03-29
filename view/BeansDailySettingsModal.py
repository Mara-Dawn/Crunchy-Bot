from typing import List
import discord

from BotSettings import BotSettings
from MaraBot import MaraBot

class BeansDailySettingsModal(discord.ui.Modal, title='Beans Settings'):
    beans_daily_min = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.BEANS_DAILY_MIN)
    beans_daily_max = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.BEANS_DAILY_MAX)
    beans_bonus_count = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.BEANS_BONUS_CARD_COUNT)
    beans_bonus_amount = discord.ui.TextInput(label='', required=False, custom_id=BotSettings.BEANS_BONUS_CARD_AMOUNT)

    def __init__(self, bot: MaraBot, settings: BotSettings):
        super().__init__()
        
        self.settings = settings
        self.bot = bot
        self.command = 'beans daily setup'

        self.beans_daily_min.label = self.settings.get_setting_title(BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MIN)
        self.beans_daily_max.label = self.settings.get_setting_title(BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MAX)
        self.beans_bonus_count.label = self.settings.get_setting_title(BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_COUNT)
        self.beans_bonus_amount.label = self.settings.get_setting_title(BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_AMOUNT)
    
    async def on_submit(self, interaction: discord.Interaction):
        text_inputs = [
            self.beans_daily_min,
            self.beans_daily_max,
            self.beans_bonus_count,
            self.beans_bonus_amount
        ]
        errors: List[discord.ui.TextInput] = []
        
        for text_input in text_inputs:
            if not text_input.value.lstrip('-').isdigit():
                errors.append(text_input)
                
        if len(errors) != 0:
            message = f'Illegal values:\n{', \n'.join([f'{text_input.label}({text_input.value})' for text_input in errors])}'
            await self.bot.response('Beans', interaction, message, self.command, args=[text_input.label for text_input in text_inputs])
            return
        
        if self.beans_daily_min.value > self.beans_daily_max.value :
            await self.bot.response('Beans', interaction, f'Beans minimum must be smaller than Beans maximum.', self.command, args=[text_input.label for text_input in text_inputs])
            return
            
        self.settings.set_beans_daily_min(interaction.guild_id, int(self.beans_daily_min.value))
        self.settings.set_beans_daily_max(interaction.guild_id, int(self.beans_daily_max.value))
        self.settings.set_beans_bonus_count(interaction.guild_id, int(self.beans_bonus_count.value))
        self.settings.set_beans_bonus_amount(interaction.guild_id, int(self.beans_bonus_amount.value))
        
        await self.bot.response('Beans', interaction, f'Settings were successfully updated.', self.command, args=[text_input.value for text_input in text_inputs])