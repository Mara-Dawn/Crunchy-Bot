import discord
from combat.gear.gear import Gear
from discord.ext import commands


class SpecialShopHeadEmbed(discord.Embed):

    def __init__(
        self,
        bot: commands.Bot,
    ):
        description = "Definitely not Ethel's smuggled wares.\n"
        description += "Resets daily with three random items for you to buy."

        description = f"```{description}```"

        super().__init__(
            title="Secret Shop",
            color=discord.Colour.purple(),
            description=description,
        )
        author_name = bot.user.display_name
        author_img = bot.user.display_avatar
        self.set_author(name=author_name, icon_url=author_img)
        self.set_image(url="https://i.imgur.com/HxKE6mf.png")


class SpecialShopEndEmbed(discord.Embed):

    def __init__(
        self,
        bot: commands.Bot,
    ):
        super().__init__(
            title="",
            color=discord.Colour.purple(),
            description="",
        )
        author_name = bot.user.display_name
        author_img = bot.user.display_avatar
        self.set_author(name=author_name, icon_url=author_img)
        self.set_thumbnail(url=author_img)
        self.set_image(url="https://i.imgur.com/HxKE6mf.png")
