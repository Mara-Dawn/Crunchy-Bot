import discord


class PlotEmbed(discord.Embed):

    def __init__(
        self,
        x: int,
        y: int,
        author: str,
    ):
        super().__init__(
            title=f"Plot ({x},{y})",
            color=discord.Colour.purple(),
            description="Take care of your plant on this plot.",
        )
        self.set_author(name=author, icon_url="attachment://profile_picture.png")

        self.set_image(url="attachment://status.png")
