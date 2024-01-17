import discord

from discord.ext import commands
from logger import BotLogger
from settings import BotSettings
from userlist import UserList

class Police(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        self.naughty_list = {}
        self.logger = bot.logger
        self.settings = bot.settings

    @commands.Cog.listener()
    async def on_ready(self):

        for guild in self.bot.guilds:
            self.naughty_list[guild.id] = UserList()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        self.naughty_list[guild.id] = UserList()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        del self.naughty_list[guild.id]

    @commands.Cog.listener()
    async def on_message(self, message):

        author_id = message.author.id
        guild_id = message.guild.id

        if author_id == self.bot.user.id:
            return
        
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

            difference = message.created_at - naughty_user.get_timestamp()
            remaining = self.settings.get_timeout(guild_id) - int(difference.total_seconds())

            if difference.total_seconds() < self.settings.get_timeout(guild_id):

                self.logger.debug(guild_id, f'User rate limit active for {message.author.name}. {remaining} seconds remaining.')

                if not naughty_user.was_notified():

                    self.logger.debug(guild_id, f'User {message.author.name} was notified.')
                    await message.channel.send(f'<@{author_id}> {self.settings.get_timeout_notice(guild_id)} try again in {remaining} seconds.')
                    naughty_list.mark_as_notified(author_id)

                await message.delete()

                if self.settings.get_refresh_timeout_enabled(guild_id):

                    self.logger.debug(guild_id, f'User {message.author.name} rate limit was reset.')
                    naughty_list.update_user(author_id, message.created_at)

            else:

                self.logger.debug(guild_id, f'User {message.author.name} rate limit was reset.')
                naughty_list.update_user(author_id, message.created_at)

    @commands.command()
    async def set(self, ctx: commands.Context, num: int):
        await ctx.send("test")

        
async def setup(bot):
    await bot.add_cog(Police(bot))
