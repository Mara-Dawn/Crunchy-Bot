import discord

from control.controller import Controller
from control.event_manager import EventManager
from view.ranking_embed import RankingEmbed
from view.types import RankingType


class RankingView(discord.ui.View):

    def __init__(self, controller: Controller, interaction: discord.Interaction):
        self.interaction = interaction
        self.controller = controller
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        super().__init__(timeout=100)
        self.add_item(Dropdown())

    async def edit_page(
        self, interaction: discord.Interaction, ranking_type: RankingType
    ):
        image = "./img/jail_wide.png"

        ranking_data = self.event_manager.get_user_rankings(
            interaction.guild_id, ranking_type
        )
        ranking_img = discord.File(image, "ranking_img.png")
        police_img = discord.File("./img/police.png", "police.png")
        embed = RankingEmbed(
            self.controller.bot, interaction, ranking_type, ranking_data
        )
        await interaction.response.edit_message(
            embed=embed, view=self, attachments=[police_img, ranking_img]
        )

    # pylint: disable-next=arguments-differ
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            embed = discord.Embed(
                description="Only the author of the command can perform this action.",
                color=16711680,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

    async def on_timeout(self):
        # remove buttons on timeout
        message = await self.interaction.original_response()
        await message.edit(view=None)


class Dropdown(discord.ui.Select):

    def __init__(self):
        options = [
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.BEANS],
                description="Who has the biggest bean?",
                emoji="🅱️",
                value=RankingType.BEANS,
            ),
            # discord.SelectOption(label=RankingEmbed.TITLES[RankingType.TOTAL_GAMBAD_SPENT], description='Who is the biggest gamba addict?', emoji='🅱️', value=RankingType.TOTAL_GAMBAD_SPENT),
            # discord.SelectOption(label=RankingEmbed.TITLES[RankingType.TOTAL_GAMBAD_WON], description='Who won the most beans?', emoji='🅱️', value=RankingType.TOTAL_GAMBAD_WON),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.MIMICS],
                description="Who gets vored the most?",
                emoji="🧰",
                value=RankingType.MIMICS,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.SPAM_SCORE],
                description="Who is the biggest spammer?",
                emoji="📢",
                value=RankingType.SPAM_SCORE,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.SLAP],
                description="Who slapped the most users?",
                emoji="✋",
                value=RankingType.SLAP,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.PET],
                description="Who petted the most users?",
                emoji="🥰",
                value=RankingType.PET,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.FART],
                description="Who farted on the most users?",
                emoji="💩",
                value=RankingType.FART,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.SLAP_RECIEVED],
                description="Who was slapped the most?",
                emoji="💢",
                value=RankingType.SLAP_RECIEVED,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.PET_RECIEVED],
                description="Who was petted the most?",
                emoji="💜",
                value=RankingType.PET_RECIEVED,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.FART_RECIEVED],
                description="Who was farted on the most?",
                emoji="💀",
                value=RankingType.FART_RECIEVED,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.JAIL_TOTAL],
                description="Who spent the most time in jail?",
                emoji="⏲",
                value=RankingType.JAIL_TOTAL,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.JAIL_COUNT],
                description="Who has the most jail sentences?",
                emoji="🏛",
                value=RankingType.JAIL_COUNT,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.TIMEOUT_TOTAL],
                description="Who spent the most time in timeout?",
                emoji="⏰",
                value=RankingType.TIMEOUT_TOTAL,
            ),
            discord.SelectOption(
                label=RankingEmbed.TITLES[RankingType.TIMEOUT_COUNT],
                description="Who has the most timeouts?",
                emoji="🔁",
                value=RankingType.TIMEOUT_COUNT,
            ),
        ]

        super().__init__(
            placeholder="Choose a Leaderbord",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        view: RankingView = self.view

        if await view.interaction_check(interaction):
            await view.edit_page(interaction, int(self.values[0]))
