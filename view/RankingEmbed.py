from typing import Any, List, Tuple
import discord

from BotUtil import BotUtil
from CrunchyBot import CrunchyBot
from view.RankingType import RankingType

class RankingEmbed(discord.Embed):
    
    TITLES = {
        RankingType.BEANS: "Beans Rankings (excl. Shop/Transfers)",
        RankingType.SLAP: "Slap Rankings",
        RankingType.PET: "Pet Rankings",
        RankingType.FART: "Fart Rankings",
        RankingType.SLAP_RECIEVED: "Slaps Recieved Rankings",
        RankingType.PET_RECIEVED: "Pets Recieved  Rankings",
        RankingType.FART_RECIEVED: "Farts Recieved  Rankings",
        RankingType.TIMEOUT_TOTAL: "Total Timeout Duration Rankings",
        RankingType.TIMEOUT_COUNT: "Timeout Count Rankings",
        RankingType.JAIL_TOTAL: "Total Jail Duration Rankings",
        RankingType.JAIL_COUNT: "Jail Count Rankings",
        RankingType.SPAM_SCORE: "Spam Score Rankings",
    }
    
    def __init__(self, bot: CrunchyBot,  interaction: discord.Interaction, type: RankingType, rankings: List[Tuple[int, Any]]):
        super().__init__(
            title=f"Leaderbords for {interaction.guild.name}",
            color=discord.Colour.purple(),
            description=self.TITLES[type]
        )
        
        leaderbord_msg = ''
        rank = 1
        for (id, amount) in rankings:
            leaderbord_msg += f'**{rank}.** {BotUtil.get_name(bot, interaction.guild_id, id, 100)} `{amount}`\n'
            rank += 1
            if rank == 30:
                break
        
        self.add_field(name="", value=leaderbord_msg)
        self.set_image(url="attachment://ranking_img.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
