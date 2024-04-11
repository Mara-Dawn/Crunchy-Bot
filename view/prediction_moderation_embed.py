import discord

from datalayer.prediction_stats import PredictionStats


class PredictionModerationEmbed(discord.Embed):

    ITEMS_PER_PAGE = 4

    def __init__(
        self,
        guild_name: str,
        predictions: list[PredictionStats],
        start_offset: int = 0,
    ):
        description = "Moderate the incoming Prediction suggestions from here."
        super().__init__(
            title=f"Prediction Management for {guild_name}",
            color=discord.Colour.purple(),
            description=description,
        )
        end_offset = min((start_offset + self.ITEMS_PER_PAGE), len(predictions))
        display = predictions[start_offset:end_offset]

        for prediction in display:
            self.add_field(
                name="",
                value="|",
                inline=False,
            )
            prediction.add_to_embed(self, 44, moderator=True)

        if len(predictions) == 0:
            self.add_field(
                name="> Empty",
                value="No results were found for your selected filter.",
                inline=False,
            )

        self.set_image(url="attachment://menu_img.png")
        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
