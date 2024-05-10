from typing import Any

import discord
from datalayer.ranking import Ranking
from datalayer.types import Season
from view.types import RankingType


class RankingEmbed(discord.Embed):

    def __init__(
        self,
        interaction: discord.Interaction,
        ranking_type: RankingType,
        rankings: dict[str, Any],
        season: Season,
    ):
        super().__init__(
            title=f"Leaderbords for {interaction.guild.name} ({season.value})",
            color=discord.Colour.purple(),
        )
        self.add_field(
            name=Ranking.DEFINITIONS[ranking_type].title,
            value=Ranking.DEFINITIONS[ranking_type].description,
            inline=False,
        )

        leaderbord_msg = ""
        rank = 1
        for user_name, amount in rankings.items():
            leaderbord_msg += f"**{rank}.** {user_name} `{amount}`\n"
            rank += 1
            if rank == 30:
                break

        self.add_field(name="", value=leaderbord_msg)
        self.set_image(url="attachment://ranking_img.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
