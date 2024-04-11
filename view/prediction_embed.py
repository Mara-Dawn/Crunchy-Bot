import discord

from datalayer.prediction_stats import PredictionStats


class PredictionEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        guild_name: str,
        predictions: list[PredictionStats],
        user_bets: dict[int, tuple[int, int]] = None,
        start_offset: int = 0,
    ):
        description = "Get rich by making smart predictions!"
        super().__init__(
            title=f"Bean Predictions for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(predictions))
        display = predictions[start_offset:end_offset]

        for prediction in display:
            user_bet = None
            if user_bets is not None and prediction.prediction.id in user_bets:
                user_bet = user_bets[prediction.prediction.id]
            self.add_field(
                name="",
                value="|",
                inline=False,
            )
            prediction.add_to_embed(self, 44, user_bet)

        if len(predictions) == 0:
            self.add_field(
                name="> Empty",
                value="Currently there are no active predictions.",
                inline=False,
            )

        self.set_image(url="attachment://menu_img.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
