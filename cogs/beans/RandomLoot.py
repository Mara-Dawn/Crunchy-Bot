import datetime
import random
import secrets
import discord

from discord.ext import commands, tasks
from discord import app_commands
from typing import *
from BotSettings import BotSettings
from CrunchyBot import CrunchyBot
from cogs.beans.BeansGroup import BeansGroup
from view.SettingsModal import SettingsModal

class RandomLoot(BeansGroup):
    
    def __init__(self, bot: CrunchyBot):
        super().__init__(bot)
        self.lootbox_timers = {}

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __check_enabled(self, interaction: discord.Interaction) -> bool:
        guild_id = interaction.guild_id
        
        if not self.settings.get_beans_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans module is currently disabled.')
            return False
        
        if interaction.channel_id not in self.settings.get_beans_channels(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans commands cannot be used in this channel.')
            return False
        
        return True
    
    def __reevaluate_next_lootbox(self, guild_id: int):
        min_wait = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_WAIT_KEY)
        max_wait = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_WAIT_KEY)
        next_drop_delay = random.randint(min_wait, max_wait)
        self.logger.log(guild_id, f'New random lootbox interval: {next_drop_delay} minutes.', cog=self.__cog_name__)
        next_drop = datetime.datetime.now() + datetime.timedelta(minutes=next_drop_delay)
        self.lootbox_timers[guild_id] = next_drop
    
    @commands.Cog.listener('on_ready')
    async def on_ready_randomloot(self):
        self.loot_box_task.start()
        self.logger.log("init", "RandomLoot loaded.", cog=self.__cog_name__)

    @commands.Cog.listener('on_guild_join')
    async def on_guild_join_randomloot(self, guild):
        self.logger.log(guild.id, f'Adding lootbox timer for new guild.', cog=self.__cog_name__)
        self.__reevaluate_next_lootbox(guild.id)
        
    @commands.Cog.listener('on_guild_remove')
    async def on_guild_remove_randomloot(self, guild):
        del self.lootbox_timers[guild.id]
    
    @tasks.loop(minutes = 1)
    async def loot_box_task(self):
        self.logger.debug("sys", f'Lootbox task started.', cog=self.__cog_name__)
        
        for guild in self.bot.guilds:
            if datetime.datetime.now() < self.lootbox_timers[guild.id]:
                continue
            
            self.logger.log("sys", f'Lootbox timeout reached.', cog=self.__cog_name__)
            self.__reevaluate_next_lootbox(guild.id)
            
            bean_channels = self.settings.get_beans_channels(guild.id)
            if len(bean_channels) == 0:
                continue
            await self.item_manager.drop_loot_box(guild, secrets.choice(bean_channels))
            
    @loot_box_task.before_loop
    async def loot_box_task_before(self):
        self.logger.log("sys", f'Lootbox before loop started.', cog=self.__cog_name__)

        for guild in self.bot.guilds:
            min_wait = self.settings.get_setting(guild.id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_WAIT_KEY)
            max_wait = self.settings.get_setting(guild.id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_WAIT_KEY)
            next_drop_delay = random.randint(min_wait, max_wait)
            self.logger.log(guild.id, f'Random drop delay: {next_drop_delay} minutes.', cog=self.__cog_name__)
            
            loot_box_event = self.database.get_last_loot_box_event(guild.id)
            last_drop = datetime.datetime.now()
        
            if loot_box_event is not None:
                last_drop = loot_box_event.get_datetime()
            
            diff = datetime.datetime.now() - last_drop
            self.logger.log(guild.id, f'Last loot box drop was {int(diff.total_seconds()/60)} minutes ago.', cog=self.__cog_name__)
            
            next_drop = last_drop + datetime.timedelta(minutes=next_drop_delay)
            diff = next_drop - datetime.datetime.now()
            self.logger.log(guild.id, f'Next drop in {int(diff.total_seconds()/60)} minutes.', cog=self.__cog_name__)
            
            self.lootbox_timers[guild.id] = next_drop
    
    @app_commands.command(name="spawn_lootbox", description="Manually spawn a loot box in a beans channel. (Admin only)")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def spawn_lootbox(self, interaction: discord.Interaction):
        bean_channels = self.settings.get_beans_channels(interaction.guild_id)
        if len(bean_channels) == 0:
            await self.bot.command_response(self.__cog_name__, interaction, "Error: No beans channel set.")
        
        await self.item_manager.drop_loot_box(interaction.guild, secrets.choice(bean_channels))
        await self.bot.command_response(self.__cog_name__, interaction, "Loot box successfully spawned.")
        self.__reevaluate_next_lootbox(interaction.guild.id)
    
    @app_commands.command(name="lootbox_setup", description="Opens a dialog to edit various lootbox settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def lootbox_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(
            self.bot, self.settings,
            self.__cog_name__,
            interaction.command.name,
            "Settings for Lootbox related Features",
            self.__reevaluate_next_lootbox,
            [interaction.guild.id]
        )
        
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_WAIT_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_WAIT_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_BEANS_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_BEANS_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_RARE_CHANCE_KEY, float)
        
        modal.add_constraint([BotSettings.BEANS_LOOTBOX_MIN_WAIT_KEY, BotSettings.BEANS_LOOTBOX_MAX_WAIT_KEY], lambda a,b: a <= b , 'Minimum wait must be smaller than maximum.')
        modal.add_constraint([BotSettings.BEANS_LOOTBOX_MIN_BEANS_KEY, BotSettings.BEANS_LOOTBOX_MAX_BEANS_KEY], lambda a,b: a <= b , 'Minimum beans must be smaller than maximum.')
        modal.add_constraint([BotSettings.BEANS_LOOTBOX_RARE_CHANCE_KEY], lambda a: a >= 0 and a <= 1 , 'Chance must be between 0 and 1.')
        
        await interaction.response.send_modal(modal)
       
async def setup(bot):
    await bot.add_cog(RandomLoot(bot))
