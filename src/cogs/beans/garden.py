import discord
from bot import CrunchyBot
from discord import app_commands
from discord.ext import commands, tasks
from events.types import UIEventType
from events.ui_event import UIEvent
from view.garden.embed import GardenEmbed
from view.garden.plot_view import PlotView
from view.garden.view import GardenView

from cogs.beans.beans_group import BeansGroup


class Garden(BeansGroup):

    def __init__(self, bot: CrunchyBot) -> None:
        super().__init__(bot)

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __check_enabled(self, interaction: discord.Interaction) -> bool:
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_beans_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__, interaction, "Beans module is currently disabled."
            )
            return False

        if (
            interaction.channel_id
            not in await self.settings_manager.get_beans_channels(guild_id)
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans commands cannot be used in this channel.",
            )
            return False

        return True

    @commands.Cog.listener("on_ready")
    async def on_ready_garden(self):
        self.garden_view_refresh.start()
        self.logger.log("init", "Garden loaded.", cog=self.__cog_name__)

    @tasks.loop(minutes=1)
    async def garden_view_refresh(self):
        self.logger.debug(
            "sys", "Garden view refresh task started.", cog=self.__cog_name__
        )

        for view in self.controller.views:
            if isinstance(view, GardenView | PlotView):
                garden = await self.database.get_user_garden(
                    view.guild_id, view.member_id
                )
                event = UIEvent(
                    UIEventType.GARDEN_REFRESH,
                    garden,
                    view.id,
                )
                await self.controller.dispatch_ui_event(event)

    @app_commands.command(name="garden", description="Plant beans in your garden.")
    @app_commands.guild_only()
    async def garden(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        guild_id = interaction.guild_id
        user_id = interaction.user.id

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        garden = await self.database.get_user_garden(guild_id, user_id)
        embed = GardenEmbed(self.controller.bot, garden)
        view = GardenView(self.controller, interaction, garden)
        content = embed.get_garden_content()
        message = await interaction.followup.send(
            content=content, embed=embed, view=view, ephemeral=True
        )
        view.set_message(message)


async def setup(bot):
    await bot.add_cog(Garden(bot))
