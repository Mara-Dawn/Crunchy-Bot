import discord
from discord.ext import commands
from events.types import UIEventType
from events.ui_event import UIEvent
from view.ranking_embed import RankingEmbed
from view.types import RankingType

from control.controller import Controller
from control.database_manager import DatabaseManager
from control.event_manager import EventManager
from control.logger import BotLogger
from control.view.view_controller import ViewController


class RankingViewController(ViewController):

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        database: DatabaseManager,
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
                await self.update_rankings(interaction, ranking_type, event.view_id)

    async def update_rankings(
        self, interaction: discord.Interaction, ranking_type: RankingType, view_id: int
    ):
        image = "./img/jail_wide.png"

        ranking_data = self.event_manager.get_user_rankings(
            interaction.guild_id, ranking_type
        )
        ranking_img = discord.File(image, "ranking_img.png")
        police_img = discord.File("./img/police.png", "police.png")
        embed = RankingEmbed(interaction, ranking_type, ranking_data)
        await interaction.edit_original_response(
            embed=embed, attachments=[police_img, ranking_img]
        )
