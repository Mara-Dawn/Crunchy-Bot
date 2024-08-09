import datetime

import discord
from bot import CrunchyBot
from control.ai_manager import AIManager
from control.types import AIVersion
from discord import app_commands
from discord.ext import commands, tasks
from events.garden_event import GardenEvent
from events.types import GardenEventType, UIEventType
from events.ui_event import UIEvent
from view.garden.embed import GardenEmbed
from view.garden.plot_view import PlotView
from view.garden.view import GardenView

from cogs.beans.beans_group import BeansGroup


class Garden(BeansGroup):

    def __init__(self, bot: CrunchyBot) -> None:
        super().__init__(bot)
        self.ai_manager: AIManager = self.controller.get_service(AIManager)

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

    async def __beans_role_check(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        guild_id = interaction.guild_id

        beans_role = await self.settings_manager.get_beans_role(guild_id)
        if beans_role is None:
            return True
        if beans_role in [role.id for role in member.roles]:
            return True

        role_name = interaction.guild.get_role(beans_role).name
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"You can only use this command if you have the role `{role_name}`.",
        )
        return False

    @commands.Cog.listener("on_ready")
    async def on_ready_garden(self):
        # self.garden_view_refresh.start()
        self.garden_notifications.start()
        self.logger.log("init", "Garden loaded.", cog=self.__cog_name__)

    @tasks.loop(minutes=15)
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

    @tasks.loop(minutes=15)
    async def garden_notifications(self):
        self.logger.debug(
            "sys", "Garden notification task started.", cog=self.__cog_name__
        )

        for guild in self.bot.guilds:

            gardens = await self.database.get_guild_gardens(guild.id)
            for garden in gardens:
                plots = garden.notification_pending_plots()
                if len(plots) > 0:
                    user = self.bot.get_user(garden.member_id)
                    for plot in plots:
                        event = GardenEvent(
                            datetime.datetime.now(),
                            guild.id,
                            plot.garden_id,
                            plot.id,
                            garden.member_id,
                            GardenEventType.NOTIFICATION,
                        )
                        await self.controller.dispatch_event(event)
                    if user is not None:
                        self.logger.log(
                            "sys",
                            f"Sending garden notification to {user.display_name}",
                            cog=self.__cog_name__,
                        )
                        # message = (
                        #     f"Hey there, some of your plants on {guild.name} are ready to be harvested.\n"
                        #     "Make sure to drop by and visit your */beans garden* to not miss out on your rewards!"
                        # )

                        prompt = (
                            f"Please create a short notification message adressed to a user named {user.display_name}. "
                            f"Inform them about their beans garden on server {guild.name} having some plants that are ready for harvest. "
                            "Also mention that they should come visit their garden soon to take care of them so they wont miss out on the rewards. "
                        )

                        message = await self.ai_manager.prompt(
                            guild_id=guild.id,
                            name=user.display_name,
                            text_prompt=prompt,
                            ai_version=AIVersion.GPT4_O_MINI,
                        )

                        await user.send(message)

    @app_commands.command(name="garden", description="Plant beans in your garden.")
    @app_commands.guild_only()
    async def garden(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return
        if not await self.__beans_role_check(interaction):
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
