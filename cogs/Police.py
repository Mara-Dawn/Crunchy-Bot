import asyncio
import copy
import datetime
import discord

from discord.ext import commands
from discord import Message, app_commands
from typing import Dict, Literal, Optional
from BotLogger import BotLogger
from BotSettings import BotSettings
from datalayer.UserList import UserList
from datalayer.UserListNode import UserListNode

class Police(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.naughty_list: Dict[int, UserList] = {}
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings

    async def __command_response(self, interaction: discord.Interaction, message: str) -> None:
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}`.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.send_message(message, ephemeral=True)
    
    async def __has_permission(interaction: discord.Interaction) -> bool:
        
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    async def timeout_task(self, message: Message, user_node: UserListNode):
        
        channel = message.channel
        user = message.author
        guild_id = message.guild.id
        timeout_max = self.settings.get_police_timeout(guild_id)
        
        timestamp_now = int(datetime.datetime.now().timestamp())
        release = timestamp_now + timeout_max
        user_node.timeout()
        
        user_overwrites = channel.overwrites_for(user)
        initial_overwrites = copy.deepcopy(user_overwrites)
        user_overwrites.send_messages = False
        
        await message.channel.send(f'<@{user.id}> {self.settings.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=(timeout_max))
        self.logger.log(guild_id, f'Activated rate limit for {message.author.name}.')
        await message.delete()
        
        await channel.set_permissions(user, overwrite=user_overwrites)
        self.logger.log(channel.guild.id, f'Temporarily removed send_messages permission from {user.name} in {channel.name}.')
        
        timeout_length = timeout_max - (int(datetime.datetime.now().timestamp()) - timestamp_now)
        
        await asyncio.sleep(timeout_length)
        
        user_node.release()
        self.logger.log(guild_id, f'User {message.author.name} rate limit was reset.')
        
        await message.channel.set_permissions(message.author, overwrite=initial_overwrites)
        self.logger.log(guild_id, f'Reinstated old permissions for {user.name} in {channel.name}.')
        
    @commands.Cog.listener()
    async def on_ready(self):

        for guild in self.bot.guilds:
            self.naughty_list[guild.id] = UserList()
            
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        self.naughty_list[guild.id] = UserList()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        del self.naughty_list[guild.id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
       
        author_id = message.author.id
        if author_id == self.bot.user.id:
            return
        
        if len(message.content) > 0 and message.content[0] == "/":
            return
        
        if not message.guild:
            return
        
        guild_id = message.guild.id
        
        if not self.settings.get_police_enabled(guild_id):
            return
        
        if message.channel.id in self.settings.get_police_exclude_channels(guild_id):
            return
        
        naughty_list = self.naughty_list[guild_id]
        
        if bool(set([x.id for x in message.author.roles]).intersection(self.settings.get_police_naughty_roles(guild_id))):

            self.logger.debug(guild_id, f'{message.author.name} has matching roles')
            
            if not naughty_list.has_user(author_id):
                
                message_limit = self.settings.get_police_message_limit(guild_id)
                self.logger.log(guild_id, f'Added rate tracking for user {message.author.name}')
                naughty_list.add_user(author_id, message_limit)
                naughty_list.add_message(author_id, message.created_at)
                return
            
            naughty_list.add_message(author_id, message.created_at)
            
            message_limit_interval = self.settings.get_police_message_limit_interval(guild_id)
            naughty_user = naughty_list.get_user(author_id)
            
            if not naughty_user.is_in_timeout():
                
                if not naughty_user.is_spamming(message_limit_interval):
                    return
                
                self.bot.loop.create_task(self.timeout_task(message, naughty_user))
                return
                
        elif naughty_list.has_user(author_id):
            
            self.logger.log(guild_id, f'Removed rate tracing for user {message.author.name}')
            naughty_list.remove_user(author_id)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
    
    group = app_commands.Group(name="police", description="...asd")

    @app_commands.command(name="meow")
    @app_commands.check(__has_permission)
    async def meow(self, interaction: discord.Interaction) -> None:
        
        await self.__command_response(interaction, "Meow!")
        
    @group.command(name="settings")
    @app_commands.check(__has_permission)
    async def get_settings(self, interaction: discord.Interaction):
        
        output = self.settings.get_settings_string(interaction.guild_id, BotSettings.POLICE_SUBSETTINGS_KEY)
        
        await self.__command_response(interaction, output)
    
    
    @group.command(name="toggle")
    @app_commands.describe(enabled='Turns the police module on or off.')
    @app_commands.check(__has_permission)
    async def set_toggle(self, interaction: discord.Interaction, enabled: Literal['on', 'off']):
        
        self.settings.set_police_enabled(interaction.guild_id, enabled == "on")
        
        await self.__command_response(interaction, f'Police module was turned {enabled}.')
    
    
    @group.command(name="set_timeout_length")
    @app_commands.describe(length='The amount of time the users will have to wait before posting again after getting timed out. (in seconds)')
    @app_commands.check(__has_permission)
    async def set_timeout_interval(self, interaction: discord.Interaction, length: app_commands.Range[int, 0]):
        
        self.settings.set_police_timeout(interaction.guild_id, length)
        await self.__command_response(interaction, f'Timeout length set to {length} seconds.')
    
    @group.command(name="set_spam_thresholds")
    @app_commands.describe(
        message_count='Numer of messages a user may send within the specified interval.',
        interval='Time interval within the user is allowed to send message_count messages.  (in seconds)'
        )
    @app_commands.check(__has_permission)
    async def set_spam_thresholds(self, interaction: discord.Interaction, message_count: app_commands.Range[int, 1], interval: app_commands.Range[int, 1]):
        
        self.settings.set_police_message_limit(interaction.guild_id, message_count)
        self.settings.set_police_message_limit_interval(interaction.guild_id, interval)
        
        for guild_id in self.naughty_list:
            self.naughty_list[guild_id].clear()
        
        await self.__command_response(interaction, f'Rate limit updated: Users can send {message_count} messages within {interval} seconds before getting timed out.')
    
    @group.command(name="add_role")
    @app_commands.describe(role='The role that shall be tracked for spam detection.')
    @app_commands.check(__has_permission)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.add_police_naughty_role(interaction.guild_id, role.id)
        await self.__command_response(interaction, f'Added {role.name} to the list of active roles.')
        
    @group.command(name="remove_role")
    @app_commands.describe(role='Remove spam detection from this role.')
    @app_commands.check(__has_permission)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.remove_police_naughty_role(interaction.guild_id, role.id)
        await self.__command_response(interaction, f'Removed {role.name} from active roles.')
    
    @group.command(name="untrack_channel")
    @app_commands.describe(channel='Stop tracking spam for this channel.')
    @app_commands.check(__has_permission)
    async def untrack_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        self.settings.add_police_exclude_channel(interaction.guild_id, channel.id)
        await self.__command_response(interaction, f'Stopping spam detection in {channel.name}.')
        
    @group.command(name="track_channel")
    @app_commands.describe(channel='Reenable tracking spam for this channel.')
    @app_commands.check(__has_permission)
    async def track_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        
        self.settings.remove_police_exclude_channel(interaction.guild_id, channel.id)
        await self.__command_response(interaction, f'Resuming spam detection in {channel.name}.')
    
    @group.command(name="set_timeout_message")
    @app_commands.describe(message='This will be sent to the timed out person.')
    @app_commands.check(__has_permission)
    async def set_message(self, interaction: discord.Interaction, message: str):
        
        self.settings.set_police_timeout_notice(interaction.guild_id, message)
        await interaction.response.send_message(f'Timeout warning set to:\n `{message}`', ephemeral=True)
                
async def setup(bot):
    await bot.add_cog(Police(bot))
