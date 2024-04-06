from typing import Any

import discord
from discord.ext import commands

from bot_util import BotUtil
from view.types import RankingType


class RankingEmbed(discord.Embed):

    TITLES = {
        RankingType.BEANS: "Beans Rankings (excl. Shop/Transfers)",
        RankingType.MIMICS: "Mimic Count Rankings",
        RankingType.SLAP: "Slap Rankings",
        RankingType.PET: "Pet Rankings",
        RankingType.FART: "Fart Rankings",
        RankingType.SLAP_RECIEVED: "Slaps Recieved Rankings",
        RankingType.PET_RECIEVED: "Pets Recieved Rankings",
        RankingType.FART_RECIEVED: "Farts Recieved Rankings",
        RankingType.TIMEOUT_TOTAL: "Total Timeout Duration Rankings",
        RankingType.TIMEOUT_COUNT: "Timeout Count Rankings",
        RankingType.JAIL_TOTAL: "Total Jail Duration Rankings",
        RankingType.JAIL_COUNT: "Jail Count Rankings",
        RankingType.SPAM_SCORE: "Spam Score Rankings",
        RankingType.TOTAL_GAMBAD_SPENT: "Beans spent on Gamba Rankings",
        RankingType.TOTAL_GAMBAD_WON: "Beans won from Gamba Rankings",
    }

    def __init__(
        self,
        bot: commands.Bot,
        interaction: discord.Interaction,
        ranking_type: RankingType,
        rankings: list[tuple[int, Any]],
    ):
        super().__init__(
            title=f"Leaderbords for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description=self.TITLES[ranking_type],
        )

        leaderbord_msg = ""
        rank = 1
        for user_id, amount in rankings:
            leaderbord_msg += f"**{rank}.** {BotUtil.get_name(bot, interaction.guild_id, user_id, 100)} `{amount}`\n"
            rank += 1
            if rank == 30:
                break

        self.add_field(name="", value=leaderbord_msg)
        self.set_image(url="attachment://ranking_img.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
