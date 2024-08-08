from typing import Literal

import discord
from bot import CrunchyBot
from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import Season
from discord import app_commands
from discord.ext import commands, tasks
from view.ranking.embed import RankingEmbed
from view.ranking.statistics_embed import StatisticsEmbed
from view.ranking.view import RankingView
from view.types import RankingType


class Statistics(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.system_monitor.start()
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @tasks.loop(minutes=30)
    async def system_monitor(self):

        view_count = len(self.controller.views)
        view_controller_count = len(self.controller.view_controllers)
        service_count = len(self.controller.services)

        await self.controller.execute_garbage_collection()

        new_view_count = len(self.controller.views)

        if view_count != new_view_count:
            self.logger.log(
                "sys",
                f"Cleaned up {view_count-new_view_count} orphan views.",
                cog=self.__cog_name__,
            )

        self.logger.log(
            "sys",
            f"Controller stats: {service_count} services, {view_controller_count} view controllers, {new_view_count} views",
            cog=self.__cog_name__,
        )

    @commands.command()
    @commands.guild_only()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: Literal["~", "*", "^"] | None = None,
    ) -> None:

        maya = 95526988323753984
        mara = 90043934247501824
        fuzia = 106752187530481664

        if ctx.author.id not in [mara, fuzia, maya]:
            raise commands.NotOwner("You do not own this bot.")

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

    @app_commands.command(
        name="stats", description="See your or other peoples statistics."
    )
    @app_commands.describe(
        user="Leave this empty for your own statistics.",
    )
    @app_commands.guild_only()
    async def stats(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()

        jail_img = discord.File("./img/jail.png", "jail.png")

        user = user if user is not None else interaction.user
        user_id = user.id

        log_message = f"{interaction.user.name} used command `{interaction.command.name}` on {user.name}."
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

        user_statistics = await self.event_manager.get_user_statistics(user_id)

        embed = StatisticsEmbed(self.bot, interaction, user, user_statistics)

        await interaction.followup.send("", embed=embed, files=[jail_img])

    @app_commands.command(name="rankings", description="Crunchy user rankings.")
    @app_commands.guild_only()
    async def rankings(self, interaction: discord.Interaction, season: Season | None):
        await interaction.response.defer()
        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

        if season is None:
            season = Season.CURRENT

        ranking_data = await self.event_manager.get_user_rankings(
            interaction.guild_id, RankingType.BEANS, season
        )

        author_name = self.bot.user.display_name
        author_img = self.bot.user.display_avatar
        embed = RankingEmbed(
            author_name,
            author_img,
            interaction,
            RankingType.BEANS,
            ranking_data,
            season,
        )
        view = RankingView(self.controller, interaction, season)

        ranking_img = discord.File("./img/profile_picture.png", "ranking_img.png")

        match season:
            case Season.SEASON_1:
                ranking_img = discord.File(
                    "./img/seasons/season_1.png", "ranking_img.png"
                )
            case Season.CURRENT:
                ranking_img = discord.File(
                    "./img/profile_picture.png", "ranking_img.png"
                )
            case Season.ALL_TIME:
                ranking_img = discord.File("./img/treasure_open.png", "ranking_img.png")

        message = await interaction.followup.send(
            "", embed=embed, view=view, files=[ranking_img]
        )
        view.set_message(message)


async def setup(bot):
    await bot.add_cog(Statistics(bot))
