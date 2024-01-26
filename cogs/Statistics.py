import typing
import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal, Optional
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.BotEventManager import BotEventManager
from view.RankingEmbed import RankingEmbed
from view.RankingType import RankingType
from view.RankingView import RankingView
from view.StatisticsEmbed import StatisticsEmbed

class Statistics(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: BotEventManager = bot.event_manager
        
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
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
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)

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
    
    @app_commands.command(name="stats", description='See your or other peoples statistics.')
    @app_commands.describe(
        user='Leave this empty for your own statistics.',
        )
    @app_commands.guild_only()
    async def stats(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
        
        await interaction.response.defer()
        
        police_img = discord.File("./img/police.png", "police.png")
        jail_img = discord.File("./img/jail.png", "jail.png")
        
        user = user if user is not None else interaction.user
        user_id = user.id
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}` on {user.name}.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        
        user_statistics = self.event_manager.get_user_statistics(user_id)
        
        embed = StatisticsEmbed(self.bot, interaction, user, user_statistics)
        
        await interaction.followup.send("", embed=embed, files=[police_img, jail_img])
    
    @app_commands.command(name="rankings", description='Crunchy user rankings.')
    @app_commands.guild_only()
    async def rankings(self, interaction: discord.Interaction):
        
        log_message = f'{interaction.user.name} used command `{interaction.command.name}`.'
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer()
        
        police_img = discord.File("./img/police.png", "police.png")
        jail_wide_img = discord.File("./img/jail_wide.png", "jail_wide.png")
        ranking_data = self.event_manager.get_user_rankings(interaction.guild_id)
        
        embed = RankingEmbed(self.bot, interaction, ranking_data, RankingType.SLAP)
        view = RankingView(self.bot, interaction, ranking_data)
        
        await interaction.followup.send("",embed=embed, view=view, files=[police_img,jail_wide_img])
    
async def setup(bot):
    await bot.add_cog(Statistics(bot))
