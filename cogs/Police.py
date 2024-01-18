import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal, Optional
from logger import BotLogger
from settings import BotSettings
from userlist import UserList

class Police(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
        self.naughty_list: Dict[int, UserList] = {}
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings

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
        
        if not self.settings.get_enabled(guild_id):
            return
        
        naughty_list = self.naughty_list[guild_id]

        self.logger.debug(guild_id, f'author roles: {[x.id for x in message.author.roles]}')
        self.logger.debug(guild_id, f'settings: {self.settings.get_naughty_roles(guild_id)}')
        
        if bool(set([x.id for x in message.author.roles]).intersection(self.settings.get_naughty_roles(guild_id))):

            self.logger.debug(guild_id, f'{message.author.name} has matching roles')

            if not naughty_list.has_user(author_id):

                self.logger.debug(guild_id, f'added rate limit to user {message.author.name}')
                naughty_list.update_user(author_id, message.created_at)
                
                return

            naughty_user = naughty_list.get_user(author_id)
            
            timeout = self.settings.get_timeout(guild_id)
            
            difference = message.created_at - naughty_user.get_timestamp()
            remaining = timeout - int(difference.total_seconds())
            release = int(naughty_user.get_timestamp().timestamp()) + timeout

            if difference.total_seconds() < self.settings.get_timeout(guild_id):

                self.logger.debug(guild_id, f'User rate limit active for {message.author.name}. {remaining} seconds remaining.')

                if not naughty_user.was_notified():

                    self.logger.debug(guild_id, f'User {message.author.name} was notified.')
                    await message.channel.send(f'<@{author_id}> {self.settings.get_timeout_notice(guild_id)} Try again <t:{release}:R>.', delete_after=remaining)
                    naughty_list.mark_as_notified(author_id)

                await message.delete()

                if self.settings.get_refresh_timeout_enabled(guild_id):

                    self.logger.debug(guild_id, f'User {message.author.name} rate limit was reset.')
                    naughty_list.update_user(author_id, message.created_at)

            else:

                self.logger.debug(guild_id, f'User {message.author.name} rate limit was reset.')
                naughty_list.update_user(author_id, message.created_at)

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
    
    async def has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    group = app_commands.Group(name="police", description="...asd")

    @app_commands.command(name="meow")
    @app_commands.check(has_permission)
    async def meow(self, interaction: discord.Interaction) -> None:
        
        await interaction.response.send_message("Meow!", ephemeral=True)
        
    @group.command(name="set_interval")
    @app_commands.describe(
        interval='Time interval the users will have to wait before posting again. (in seconds)'
    )
    @app_commands.check(has_permission)
    async def set_interval(self, interaction: discord.Interaction, interval: app_commands.Range[int, 0]):
        
        self.settings.set_timeout(interaction.guild_id, interval)
        await interaction.response.send_message(f'Timeout interval set to {interval} seconds.', ephemeral=True)
        
    @group.command(name="add_role")
    @app_commands.describe(
        role='The role that shall be rate limited.'
    )
    @app_commands.check(has_permission)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.add_naughty_role(interaction.guild_id, role.id)
        await interaction.response.send_message(f'Added {role.name} to the list of active roles.', ephemeral=True)
        
    @group.command(name="remove_role")
    @app_commands.describe(
        role='Remove this role from the active list.'
    )
    @app_commands.check(has_permission)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role):
        
        self.settings.remove_naughty_role(interaction.guild_id, role.id)
        await interaction.response.send_message(f'Removed {role.name} from active roles.', ephemeral=True)
        
    @group.command(name="settings")
    @app_commands.check(has_permission)
    async def settings(self, interaction: discord.Interaction):
        
        roles = self.settings.get_naughty_roles(interaction.guild_id)
        role_str = " " + ", ".join([interaction.guild.get_role(id).name for id in roles])
        
        output = f'Active roles: `{role_str}` \n'
        output += f'Timeout(s): `{self.settings.get_timeout(interaction.guild_id)}` \n'
        output += f'Message: `{self.settings.get_timeout_notice(interaction.guild_id)}`'
        
        await interaction.response.send_message(output, ephemeral=True)
    
        
    @group.command(name="set_timeout_message")
    @app_commands.describe(
        message='This will be sent to the timed out person.'
    )
    @app_commands.check(has_permission)
    async def set_message(self, interaction: discord.Interaction, message: str):
        self.settings.set_timeout_notice(interaction.guild_id, message)
        await interaction.response.send_message(f'Timeout warning set to:\n `{message}`', ephemeral=True)
                
async def setup(bot):
    await bot.add_cog(Police(bot))
