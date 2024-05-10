import discord
from datalayer.database import Database
from datalayer.types import Season
from discord.ext import commands
from events.types import UIEventType
from events.ui_event import UIEvent
from view.ranking.embed import RankingEmbed
from view.types import RankingType

from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


class RankingViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: Database,
        controller: Controller,
    ):
        super().__init__(bot, logger, database)
        self.controller = controller
        self.event_manager: EventManager = controller.get_service(EventManager)

    async def listen_for_ui_event(self, event: UIEvent):
        match event.type:
            case UIEventType.UPDATE_RANKINGS:
                interaction = event.payload[0]
                ranking_type = event.payload[1]
                season = event.payload[2]
                await self.update_rankings(interaction, ranking_type, season)

    async def update_rankings(
        self,
        interaction: discord.Interaction,
        ranking_type: RankingType,
        season: Season,
    ):
        image = "./img/jail_wide.png"

        ranking_data = await self.event_manager.get_user_rankings(
            interaction.guild_id, ranking_type, season
        )
        ranking_img = discord.File(image, "ranking_img.png")
        police_img = discord.File("./img/police.png", "police.png")
        embed = RankingEmbed(interaction, ranking_type, ranking_data, season)
        await interaction.edit_original_response(
            embed=embed, attachments=[police_img, ranking_img]
        )
