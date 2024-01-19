import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal, Optional
from logger import BotLogger
from BotSettings import BotSettings
from datalayer.UserList import UserList

class Police(commands.Cog):
    
    def __init__(self, bot):
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
        
        naughty_list = self.naughty_list[guild_id]
        
        if bool(set([x.id for x in message.author.roles]).intersection(self.settings.get_police_naughty_roles(guild_id))):

            self.logger.log(guild_id, f'{message.author.name} has matching roles')
            
            if not naughty_list.has_user(author_id):
                
                message_limit = self.settings.get_police_message_limit(guild_id)
                self.logger.log(guild_id, f'Added rate tracing for user {message.author.name}')
                naughty_list.add_user(author_id, message_limit)
                naughty_list.add_message(author_id, message.created_at)
                return
            
            naughty_list.add_message(author_id, message.created_at)
            
            message_limit_interval = self.settings.get_police_message_limit_interval(guild_id)
            naughty_user = naughty_list.get_user(author_id)
            timeout_max = self.settings.get_police_timeout(guild_id)
            
            if not naughty_user.is_in_timeout():
                
                if not naughty_user.is_spamming(message_limit_interval):
                    return
                
                release = int(message.created_at.timestamp()) + timeout_max
                await message.channel.send(f'<@{author_id}> {self.settings.get_police_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=(timeout_max-2))
                
                naughty_user.timeout(message.created_at)
                
                self.logger.log(guild_id, f'Activated rate limit for {message.author.name}.')
                await message.delete()
                return
            
            
            timeout_duration = message.created_at - naughty_user.get_timestamp()
            
            if timeout_duration.total_seconds() < timeout_max:

                remaining = timeout_max - int(timeout_duration.total_seconds())
                self.logger.log(guild_id, f'User rate limit activated for {message.author.name}. {remaining} seconds remaining.')
                await message.delete()
                return


            self.logger.log(guild_id, f'User {message.author.name} rate limit was reset.')
            naughty_user.release()
                
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
        
    @group.command(name="get_settings")
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
    @app_commands.describe(interval='The amount of time the users will have to wait before posting again after getting timed out. (in seconds)')
    @app_commands.check(__has_permission)
    async def set_timeout_interval(self, interaction: discord.Interaction, interval: app_commands.Range[int, 0]):
        
        self.settings.set_police_timeout(interaction.guild_id, interval)
        await self.__command_response(interaction, f'Timeout length set to {interval} seconds.')
    
    @group.command(name="set_rate_limit")
    @app_commands.describe(
        message_count='Numer of messages a user may send within the specified interval.',
        interval='Time interval within the user is allowed to send message_count messages.  (in seconds)'
        )
    @app_commands.check(__has_permission)
    async def set_rate_limit(self, interaction: discord.Interaction, message_count: app_commands.Range[int, 1], interval: app_commands.Range[int, 1]):
        
        self.settings.set_police_message_limit(interaction.guild_id, message_count)
        self.settings.set_police_message_limit_interval(interaction.guild_id, interval)
        await self.__command_response(interaction, f'Rate limit updated: Users can send {message_count} messages within {interval} seconds before getting timed out.')
    
    @group.command(name="add_role")
    @app_commands.describe(role='The role that shall be rate limited.')
    @app_commands.check(__has_permission)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.add_police_naughty_role(interaction.guild_id, role.id)
        await self.__command_response(interaction, f'Added {role.name} to the list of active roles.')
        
    @group.command(name="remove_role")
    @app_commands.describe(role='Remove this role from the active list.')
    @app_commands.check(__has_permission)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.remove_naughty_role(interaction.guild_id, role.id)
        await self.__command_response(interaction, f'Removed {role.name} from active roles.')
        
    @group.command(name="set_timeout_message")
    @app_commands.describe(message='This will be sent to the timed out person.')
    @app_commands.check(__has_permission)
    async def set_message(self, interaction: discord.Interaction, message: str):
        
        self.settings.set_police_timeout_notice(interaction.guild_id, message)
        await interaction.response.send_message(f'Timeout warning set to:\n `{message}`', ephemeral=True)
                
async def setup(bot):
    await bot.add_cog(Police(bot))
