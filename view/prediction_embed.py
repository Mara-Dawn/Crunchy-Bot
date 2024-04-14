import discord


class PredictionEmbed(discord.Embed):

    def __init__(
        self,
        guild_name: str,
    ):
        description = "Get rich by making smart predictions!"
        super().__init__(
            title=f"Bean Predictions for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )

        message = (
            "Browse through the different predictions below and place your bets. "
            "\nYou can see the amount of beans already placed below each outcome."
            "\nThe odds will tell you how big your payout is gonna be relative to your bet."
        )

        self.add_field(
            name="",
            value=f"```{message}```",
            inline=False,
        )
        self.set_author(name="Crunchy Patrol")