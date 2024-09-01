from typing import Any

import discord

from datalayer.ranking import Ranking
from view.types import RankingType


class RankingEmbed(discord.Embed):

    def __init__(
        self,
        author_name,
        author_img,
        interaction: discord.Interaction,
        ranking_type: RankingType,
        rankings: dict[str, Any],
        season: int,
    ):
        season_title = f"Season {season}" if season is not None else "Current Season"

        super().__init__(
            title=f"Leaderbords for {interaction.guild.name} ({season_title})",
            color=discord.Colour.purple(),
        )
        self.set_author(name=author_name, icon_url=author_img)
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
        self.set_image(url=author_img)
