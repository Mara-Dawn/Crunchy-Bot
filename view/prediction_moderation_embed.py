import discord


class PredictionModerationEmbed(discord.Embed):

    ITEMS_PER_PAGE = 3

    def __init__(
        self,
        guild_name: str,
    ):
        description = "Moderate the incoming Prediction suggestions from here."
        super().__init__(
            title=f"Prediction Management for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )

        message = "Browse through the different predictions below to moderate them.\nAt the bottom you can filter the predictions by different states, approve or deny them and even edit not yet approved ones."

        self.add_field(
            name="",
            value=f"```{message}```",
            inline=False,
        )

        self.set_author(name="Crunchy Patrol")
