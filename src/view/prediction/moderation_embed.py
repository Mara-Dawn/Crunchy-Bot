import discord


class PredictionModerationEmbed(discord.Embed):

    ITEMS_PER_PAGE = 3

    def __init__(
        self,
        author_name,
        author_img,
        guild_name: str,
    ):
        description = "Moderate the incoming Prediction suggestions from here."
        super().__init__(
            title=f"Prediction Management for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_author(name=author_name, icon_url=author_img)

        message = "Browse through the different predictions below to moderate them.\nAt the bottom you can filter the predictions by different states, approve or deny them and even edit not yet approved ones."

        self.add_field(
            name="",
            value=f"```{message}```",
            inline=False,
        )
