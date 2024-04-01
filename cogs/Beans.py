import asyncio
import datetime
import random
import secrets
import typing
import discord

from discord.ext import commands, tasks
from discord import app_commands
from typing import *
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from CrunchyBot import CrunchyBot
from RoleManager import RoleManager
from datalayer.Database import Database
from events.BeansEventType import BeansEventType
from events.EventManager import EventManager
from shop.ItemManager import ItemManager
from shop.ItemType import ItemType
from view.SettingsModal import SettingsModal

class Beans(commands.Cog):
    
    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: EventManager = bot.event_manager
        self.role_manager: RoleManager = bot.role_manager
        self.item_manager: ItemManager = bot.item_manager
        self.lootbox_timers = {}

    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        
        if not self.settings.get_beans_enabled(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans module is currently disabled.')
            return False
        
        if interaction.channel_id not in self.settings.get_beans_channels(guild_id):
            await self.bot.command_response(self.__cog_name__, interaction, f'Beans commands cannot be used in this channel.')
            return False
        
        return True

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
    
    def __reevaluate_next_lootbox(self, guild_id: int):
        min_wait = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MIN_WAIT_KEY)
        max_wait = self.settings.get_setting(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_LOOTBOX_MAX_WAIT_KEY)
        next_drop_delay = random.randint(min_wait, max_wait)
        self.logger.log(guild_id, f'New random lootbox interval: {next_drop_delay} minutes.', cog=self.__cog_name__)
        next_drop = datetime.datetime.now() + datetime.timedelta(minutes=next_drop_delay)
        self.lootbox_timers[guild_id] = next_drop
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.lottery_task.start()
        self.loot_box_task.start()
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.logger.log(guild.id, f'Adding lootbox timer for new guild.', cog=self.__cog_name__)
        self.__reevaluate_next_lootbox(guild.id)
        
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
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
    
    @tasks.loop(time=datetime.time(hour=12, tzinfo=datetime.timezone.utc))
    async def lottery_task(self):
        
        self.logger.log("sys", f'Lottery task started.', cog=self.__cog_name__)
        
        if datetime.datetime.today().weekday() != 5:
            # only on saturdays
            self.logger.log("sys", f'Not saturday so skipping.', cog=self.__cog_name__)
            return
        
        for guild in self.bot.guilds:
            await self.__draw_lottery(guild)
        

    @app_commands.command(name="gamba", description='Gamba away your beans.')
    @app_commands.guild_only()
    async def gamba(self, interaction: discord.Interaction, amount: typing.Optional[int] = None):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        beans_gamba_min = self.settings.get_beans_gamba_min(guild_id)
        beans_gamba_max = self.settings.get_beans_gamba_max(guild_id)
        default_cooldown = self.settings.get_beans_gamba_cooldown(guild_id)
        timestamp_now = int(datetime.datetime.now().timestamp())

        if amount is not None:
            if not (beans_gamba_min <= amount and amount <= beans_gamba_max):
                await self.bot.command_response(self.__cog_name__, interaction, f'Between `🅱️{beans_gamba_min}` and `🅱️{beans_gamba_max}` you fucking monkey.', ephemeral=False)
                return 
            
        await interaction.response.defer()

        default_amount = self.settings.get_beans_gamba_cost(guild_id)
        
        if amount is None:
            amount = default_amount

        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        if current_balance < amount:
            await self.bot.command_response(self.__cog_name__, interaction, f'You\'re out of beans, idiot.', ephemeral=False)
            return
        
        last_gamba_cost_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.GAMBA_COST)
        last_gamba_payout_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.GAMBA_PAYOUT)
        
        if last_gamba_cost_event is not None: 
        
            current_date = datetime.datetime.now()
            last_gamba_beans_date = last_gamba_cost_event.get_datetime()
            
            delta = current_date - last_gamba_beans_date
            delta_seconds = delta.total_seconds()
            
            last_gamba_amount = abs(last_gamba_cost_event.get_value())
            cooldown = default_cooldown 
            
            if last_gamba_payout_event.get_value() != 0:
                #only go on cooldown when previous gamba was a win
                cooldown = default_cooldown * (last_gamba_amount / default_amount) 

            if delta_seconds <= cooldown:
                remaining = cooldown - delta_seconds
                cooldowntimer = int(timestamp_now + remaining)
                
                await self.bot.command_response(self.__cog_name__, interaction, f'Gamba is on cooldown. Try again in <t:{cooldowntimer}:R>.', ephemeral=False)
                message = await interaction.original_response()
                channel_id = message.channel.id
                message_id = message.id
                
                await asyncio.sleep(remaining)
                
                message = await self.bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
                await message.delete()
                return
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_COST, 
            user_id,
            -amount
        )
        
        response = f'You paid `🅱️{amount}` beans to gamba.'
        
        display_values = [
            '\n**0x**',
            '\n**2x**🎲',
            '\n**3x**🎲🎲',
            '\n**10x**🎲🎲🎲',
            '\n**100x**🎲🎲🎲🎲'
        ]
        
        payout = 0
        
        loss = 0.50 
        doubling = 0.33 
        tripling = 0.15
        tenfold = 0.019 
        jackpot = 0.001
        
        # (0.33*2)+(0.15*3)+(0.019*10)+(0.001*100)
        result = random.random()
        
        if result <= loss:
            final_display = 0
            final = f'\nYou lost. It is what it is.'
        elif result > loss and result <= (loss+doubling):
            final_display = 1
            payout = amount * 2
            final = f'\nYou won! Your payout is `🅱️{payout}` beans.'
        elif result > (loss+doubling) and result <= (loss+doubling+tripling):
            final_display = 2
            payout = amount * 3
            final = f'\nWow you got lucky! Your payout is `🅱️{payout}` beans.'
        elif result > (loss+doubling+tripling) and result <= (1-jackpot):
            final_display = 3
            payout = amount * 10
            final = f'\n**BIG WIN!** Your payout is `🅱️{payout}` beans.'
        elif result > (1-jackpot) and result <= 1:
            final_display = 4
            payout = amount * 100
            final = f'\n**JACKPOT!!!** Your payout is `🅱️{payout}` beans.'
        
        display = display_values[0]
        await self.bot.command_response(self.__cog_name__, interaction, response, ephemeral=False)
        
        message = await interaction.original_response()
        i = 0
        current = i
        while i <= 10 or current != final_display:
            current = i % len(display_values)
            display = display_values[current]
            await asyncio.sleep((1/20)*i)
            await message.edit(content=response+display)
            i += 1
        
        today = datetime.datetime.now().date()
        today_timestamp = datetime.datetime(year=today.year, month=today.month, day=today.day).timestamp()
        
        user_daily_gamba_count = self.database.get_beans_daily_gamba_count(guild_id, user_id, BeansEventType.GAMBA_COST, default_amount, today_timestamp)
        beans_bonus_amount = 0
        match user_daily_gamba_count:
            case 10:
                beans_bonus_amount = self.settings.get_beans_bonus_amount_10(interaction.guild_id)
            case 25:
                beans_bonus_amount = self.settings.get_beans_bonus_amount_25(interaction.guild_id)
        
        if beans_bonus_amount > 0:
            final += f'\n🎉 You reached **{user_daily_gamba_count}** gambas for today! Enjoy these bonus beans `🅱️{beans_bonus_amount}` 🎉'
            self.event_manager.dispatch_beans_event(
                datetime.datetime.now(), 
                guild_id, 
                BeansEventType.BONUS_PAYOUT, 
                user_id,
                beans_bonus_amount
            )
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.GAMBA_PAYOUT, 
            user_id,
            payout
        )
        cooldowntimer = int(default_cooldown*amount/default_amount)
        if payout == 0:
            cooldowntimer = int(default_cooldown)
        remaining = int(timestamp_now+cooldowntimer)
        timer =f'\nYou can gamble again <t:{remaining}:R>.'
        await message.edit(content=response+display+final+timer)
        channel_id = message.channel.id
        message_id = message.id
        await asyncio.sleep(max(0,cooldowntimer-10))
        message = await self.bot.get_guild(guild_id).get_channel(channel_id).fetch_message(message_id)
        await message.edit(content=response+display+final)
        
        
    group = app_commands.Group(name="beans", description="Subcommands for the Beans module.")
    
    @group.command(name="please", description='Your daily dose of beans.')
    @app_commands.guild_only()
    async def please(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return 
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        last_daily_beans_event = self.database.get_last_beans_event(guild_id, user_id, BeansEventType.DAILY)
        
        if last_daily_beans_event is not None: 
        
            current_date = datetime.datetime.now().date()
            last_daily_beans_date = last_daily_beans_event.get_datetime().date()
        
            if current_date == last_daily_beans_date:
                await self.bot.command_response(self.__cog_name__, interaction, f'You already got your daily beans, dummy! Try again tomorrow.', ephemeral=False)
                return
        
        beans_daily_min = self.settings.get_beans_daily_min(guild_id)
        beans_daily_max = self.settings.get_beans_daily_max(guild_id)

        amount = random.randint(beans_daily_min, beans_daily_max)
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id, 
            BeansEventType.DAILY, 
            user_id, 
            amount
        )
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> got their daily dose of `🅱️{amount}` beans.', args=[amount], ephemeral=False)
    
    @group.command(name="balance", description='Your current bean balance.')
    @app_commands.describe(
        user='Optional, check this users bean balance.'
        )
    @app_commands.guild_only()
    async def balance(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
        if not await self.__check_enabled(interaction):
            return 
        
        user = user if user is not None else interaction.user
        user_id = user.id
        
        guild_id = interaction.guild_id
        
        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        await self.bot.command_response(self.__cog_name__, interaction, f'<@{user_id}> currently has `🅱️{current_balance}` beans.', args=[user.display_name], ephemeral=False)
    
    @group.command(name="grant", description="Give or remove beans from specific users. (Admin only)")
    @app_commands.describe(
        user='User to give beans to.',
        amount='Amount of beans, can be negative.'
        )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def grant(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        
        guild_id = interaction.guild_id
        
        self.event_manager.dispatch_beans_event(
            datetime.datetime.now(), 
            guild_id,
            BeansEventType.BALANCE_CHANGE, 
            user.id,
            amount
        )
        
        response = f'`🅱️{abs(amount)}` beans were '
        if amount >= 0:
            response += 'added to '
        else:
            response += 'subtracted from '
        
        response += f'<@{user.id}>\'s bean balance by <@{interaction.user.id}>'
            
        await self.bot.command_response(self.__cog_name__, interaction, response, args=[user.display_name, amount], ephemeral=False)
    
    @group.command(name="transfer", description="Transfer your beans to other users.")
    @app_commands.describe(
        user='User to transfer beans to.',
        amount='Amount of beans.'
        )
    @app_commands.guild_only()
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: app_commands.Range[int, 1]):
        await interaction.response.defer()
        
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        
        current_balance = self.database.get_member_beans(guild_id, user_id)
        
        if current_balance < amount:
            await self.bot.command_response(self.__cog_name__, interaction, f'You dont have that many beans, idiot.', ephemeral=False)
            return
        now = datetime.datetime.now()
        
        self.event_manager.dispatch_beans_event(
            now, 
            guild_id,
            BeansEventType.USER_TRANSFER, 
            interaction.user.id,
            -amount
        )
        
        self.event_manager.dispatch_beans_event(
            now, 
            guild_id,
            BeansEventType.USER_TRANSFER, 
            user.id,
            amount
        )
        
        response = f'`🅱️{abs(amount)}` beans were transferred from <@{interaction.user.id}> to <@{user.id}>.'
            
        await self.bot.command_response(self.__cog_name__, interaction, response, args=[interaction.user.display_name,user.display_name, amount], ephemeral=False)
    
    @group.command(name="lottery", description="Check the current pot for this weeks beans lottery.")
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
        await self.bot.command_response(self.__cog_name__, interaction, response, ephemeral=False)
        
    @group.command(name="lottery_draw", description="Manually draw the winner of this weeks bean lottery. (Admin only)")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def lottery_draw(self, interaction: discord.Interaction):
        await self.__draw_lottery(interaction.guild)
        await self.bot.command_response(self.__cog_name__, interaction, "Lottery was drawn.")
    
    @group.command(name="spawn_lootbox", description="Manually spawn a loot box in a beans channel. (Admin only)")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def spawn_lootbox(self, interaction: discord.Interaction):
        bean_channels = self.settings.get_beans_channels(interaction.guild_id)
        if len(bean_channels) == 0:
            await self.bot.command_response(self.__cog_name__, interaction, "Error: No beans channel set.")
        
        await self.item_manager.drop_loot_box(interaction.guild, secrets.choice(bean_channels))
        await self.bot.command_response(self.__cog_name__, interaction, "Loot box successfully spawned.")
        self.__reevaluate_next_lootbox(interaction.guild.id)
    
    @group.command(name="settings", description="Overview of all beans related settings and their current value.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.BEANS_SUBSETTINGS_KEY)
        await self.bot.command_response(self.__cog_name__, interaction, output)
    
    @group.command(name="toggle", description="Enable or disable the entire beans module.")
    @app_commands.describe(enabled='Turns the beans module on or off.')
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        self.settings.set_beans_enabled(interaction.guild_id, enabled == "on")
        await self.bot.command_response(self.__cog_name__, interaction, f'Beans module was turned {enabled}.', args=[enabled])
       
    @group.command(name="daily_setup", description="Opens a dialog to edit various daily and bonus beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def daily_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(self.bot, self.settings, self.__cog_name__, interaction.command.name, "Settings for Daily Beans related Features")
        
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MIN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_DAILY_MAX_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_AMOUNT_10_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_BONUS_CARD_AMOUNT_25_KEY, int)
        
        modal.add_constraint([BotSettings.BEANS_DAILY_MIN_KEY, BotSettings.BEANS_DAILY_MAX_KEY], lambda a,b: a <= b , 'Beans minimum must be smaller than Beans maximum.')
        
        await interaction.response.send_modal(modal)
        
    @group.command(name="gamba_setup", description="Opens a dialog to edit various gamba beans settings.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def gamba_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(self.bot, self.settings, self.__cog_name__, interaction.command.name, "Settings for Gamba related Features")
        
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_DEFAULT_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_COOLDOWN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_MIN_KEY, int)
        modal.add_field(guild_id, BotSettings.BEANS_SUBSETTINGS_KEY, BotSettings.BEANS_GAMBA_MAX_KEY, int)
        
        modal.add_constraint([BotSettings.BEANS_GAMBA_MIN_KEY, BotSettings.BEANS_GAMBA_MAX_KEY], lambda a,b: a <= b , 'Gamba minimum must be smaller than gamba maximum.')
        
        await interaction.response.send_modal(modal) 

    @group.command(name="lootbox_setup", description="Opens a dialog to edit various lootbox settings.")
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
        
    @group.command(name="add_channel", description='Enable beans commands for a channel.')
    @app_commands.describe(channel='The beans channel.')
    @app_commands.check(__has_permission)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.add_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Added {channel.name} to beans channels.', args=[channel.name])
        
    @group.command(name="remove_channel", description='Disable beans commands for a channel.')
    @app_commands.describe(channel='Removes this channel from the beans channels.')
    @app_commands.check(__has_permission)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.settings.remove_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(self.__cog_name__, interaction, f'Removed {channel.name} from beans channels.', args=[channel.name])
    
async def setup(bot):
    await bot.add_cog(Beans(bot))
