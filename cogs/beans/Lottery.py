import datetime
import secrets
import discord

from discord.ext import commands, tasks
from discord import app_commands
from typing import *
from BotUtil import BotUtil
from CrunchyBot import CrunchyBot
from cogs.beans.BeansGroup import BeansGroup
from events.BeansEventType import BeansEventType
from shop.ItemType import ItemType

class Lottery(BeansGroup):
    
    def __init__(self, bot: CrunchyBot):
        super().__init__(bot)

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def __draw_lottery(self, guild: discord.Guild):
        guild_id = guild.id
        base_pot = self.settings.get_beans_lottery_base_amount(guild_id)
        bean_channels = self.settings.get_beans_channels(guild_id)
        allowed_mentions = discord.AllowedMentions(roles = True)
        lottery_data = self.database.get_lottery_data(guild_id)
        total_pot = base_pot
        ticket_pool = []
        participants = len(lottery_data)
        item = self.item_manager.get_trigger_item(guild_id, ItemType.LOTTERY_TICKET)
        
        for user_id, count in lottery_data.items():
            for i in range(count):
                ticket_pool.append(user_id)
            total_pot += item.get_cost() * count
        
        lottery_role: discord.Role = await self.role_manager.get_lottery_role(guild)
        
        response = f'# Weekly Crunchy Beans Lottery \nThis weeks <@&{lottery_role.id}> has `{participants}` participants with a total pot of  `🅱️{total_pot}` beans.'
        
        if len(ticket_pool) == 0:
            self.logger.log(guild_id,"Lottery had no participants.", cog=self.__cog_name__)
            response += f'\n\nNo winner this week due to lack of participation.'
            for channel_id in bean_channels:
                channel = guild.get_channel(channel_id)
                if channel is None:
                    continue
                await channel.send(response, allowed_mentions=allowed_mentions)
            return
        
        winner = secrets.choice(ticket_pool)
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.LOTTERY_PAYOUT, 
            winner,
            total_pot
        )
        
        response += f'\n\n**The lucky winner is:**\n🎉 <@{winner}> 🎉\n **Congratulations, the `🅱️{total_pot}` beans were tansferred to your account!**\n\n Thank you for playing 😊'
        
        self.logger.log(guild_id,f"Lottery draw complete. Winner is {BotUtil.get_name(self.bot, guild_id, winner)} with a pot of {total_pot}", cog=self.__cog_name__)
        
        for channel_id in bean_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue
            await channel.send(response, allowed_mentions=allowed_mentions)
        
        for user_id, count in lottery_data.items():
            await item.use(self.role_manager, self.event_manager, guild_id, user_id, amount=count)
  
    @commands.Cog.listener('on_ready')
    async def on_ready_lottery(self):
        self.lottery_task.start()
        self.logger.log("init","Lottery loaded.", cog=self.__cog_name__)
       
    @tasks.loop(time=datetime.time(hour=12, tzinfo=datetime.timezone.utc))
    async def lottery_task(self):
        
        self.logger.log("sys", f'Lottery task started.', cog=self.__cog_name__)
        
        if datetime.datetime.today().weekday() != 5:
            # only on saturdays
            self.logger.log("sys", f'Not saturday so skipping.', cog=self.__cog_name__)
            return
        
        for guild in self.bot.guilds:
            if not self.settings.get_beans_enabled(guild.id):
                self.logger.log("sys", f'Beans module disabled.', cog=self.__cog_name__)
                return
            
            await self.__draw_lottery(guild)

    @app_commands.command(name="lottery", description="Check the current pot for this weeks beans lottery.")
    @app_commands.guild_only()
    async def lottery(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        base_pot = self.settings.get_beans_lottery_base_amount(guild_id)
        
        lottery_data = self.database.get_lottery_data(guild_id)
        total_pot = base_pot
        participants = len(lottery_data)
        item = self.item_manager.get_trigger_item(guild_id, ItemType.LOTTERY_TICKET)
        for user_id, count in lottery_data.items():
            total_pot += item.get_cost() * count
        
        today = datetime.datetime.now(datetime.UTC).date()
        saturday = today + datetime.timedelta( (5-today.weekday()) % 7 )
        next_draw = datetime.datetime(year=saturday.year, month=saturday.month, day=saturday.day, hour=12, tzinfo=datetime.UTC)
        
        response = f'This weeks lottery has `{participants}` participants with a total pot of  `🅱️{total_pot}` beans.'
        response += f'\nThe draw happens every Saturday noon at 12 PM UTC. Next draw <t:{int(next_draw.timestamp())}:R>.'
        
        if participants > 0:
            participant_list = ', '.join([BotUtil.get_name(self.bot, guild_id, k, max_len=50) + f'[{v}]' for k,v in lottery_data.items()])
            participant_list = '```Participants: ' + participant_list + '```'
            response += participant_list
            
        await self.bot.command_response(self.__cog_name__, interaction, response, ephemeral=False)
        
    @app_commands.command(name="lottery_draw", description="Manually draw the winner of this weeks bean lottery. (Admin only)")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def lottery_draw(self, interaction: discord.Interaction):
        await self.__draw_lottery(interaction.guild)
        await self.bot.command_response(self.__cog_name__, interaction, "Lottery was drawn.")
        
async def setup(bot):
    await bot.add_cog(Lottery(bot))
