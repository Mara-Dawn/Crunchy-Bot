import discord


class PredictionEmbed(discord.Embed):

    def __init__(
        self,
        author_name,
        author_img,
        guild_name: str,
    ):
        description = "Get rich by making smart predictions!"
        super().__init__(
            title=f"Bean Predictions for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        self.set_author(name=author_name, icon_url=author_img)

        message = (
            "Browse through the different predictions below and place your bets. "
            "\nYou can see the amount of beans already placed below each outcome."
            "\nThe odds will tell you how big your payout is gonna be relative to your bet."
        )
        important_info = "**New:**\nWhen a prediction submitted by you is paid out, **you will be rewarded with beans worth 5% of the total pot!**"

        self.add_field(
            name="",
            value=f"```{message}```\n{important_info}",
            inline=False,
        )
