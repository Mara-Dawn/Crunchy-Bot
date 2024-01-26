import discord
from MaraBot import MaraBot
from datalayer.UserRankings import UserRankings
from view.RankingEmbed import RankingEmbed
from view.RankingType import RankingType

class RankingView(discord.ui.View):
    def __init__(self, bot: MaraBot, interaction: discord.Interaction, ranking_data: UserRankings):
        self.interaction = interaction
        self.ranking_data = ranking_data
        self.bot = bot
        super().__init__(timeout=100)
        self.add_item(Dropdown())

    async def edit_page(self, interaction: discord.Interaction, type: RankingType):
        
        embed = RankingEmbed(self.bot, interaction, self.ranking_data, type)
        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False
    
    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)
    
class Dropdown(discord.ui.Select):
    
    def __init__(self):

        options = [
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.SLAP], description='Who slapped the most users?', emoji='✋', value=RankingType.SLAP),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.PET], description='Who petted the most users?', emoji='🥰', value=RankingType.PET),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.FART], description='Who farted on the most users?', emoji='💩', value=RankingType.FART),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.SLAP_RECIEVED], description='Who was slapped the most?', emoji='💢', value=RankingType.SLAP_RECIEVED),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.PET_RECIEVED], description='Who was petted the most?', emoji='💜', value=RankingType.PET_RECIEVED),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.FART_RECIEVED], description='Who was farted on the most?', emoji='💀', value=RankingType.FART_RECIEVED),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.JAIL_TOTAL], description='Who spent the most time in jail?', emoji='⏲', value=RankingType.JAIL_TOTAL),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.JAIL_COUNT], description='Who has the most jail sentences?', emoji='🏛', value=RankingType.JAIL_COUNT),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.TIMEOUT_TOTAL], description='Who spent the most time in timeout?', emoji='⏰', value=RankingType.TIMEOUT_TOTAL),
            discord.SelectOption(label=RankingEmbed.TITLES[RankingType.TIMEOUT_COUNT], description='Who has the most timeouts?', emoji='🔁', value=RankingType.TIMEOUT_COUNT)
        ]

        super().__init__(placeholder='Choose a Leaderbord', min_values=1, max_values=1, options=options, row=0)
    
    async def callback(self, interaction: discord.Interaction):
        
        view: RankingView = self.view
        
        if await view.interaction_check(interaction):
            await view.edit_page(interaction, int(self.values[0]))