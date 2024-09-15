import discord
from discord import app_commands
from discord.ext import commands

from bot import CrunchyBot
from control.controller import Controller
from control.event_manager import EventManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.quote import Quote
from events.quote_event import QuoteEvent
from view.image_generator import ImageGenerator


class Quotes(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )

        self.ctx_menu = app_commands.ContextMenu(
            name="Quote",
            callback=self.quote_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def quote_context_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        guild_id = interaction.guild_id

        await interaction.response.defer()

        quote = Quote(
            message.created_at,
            guild_id,
            message.author.id,
            message.author.display_name,
            interaction.user.id,
            message.id,
            message.channel.id,
            message.content,
        )

        quote_id = await self.database.log_quote(quote)

        event = QuoteEvent(message.created_at, guild_id, quote_id)
        await self.controller.dispatch_event(event)

        response = f"<@{message.author.id}> Your message {message.jump_url} was deemed quote worthy by <@{interaction.user.id}> and will be saved for the future."
        await self.bot.response(
            self.__cog_name__,
            interaction,
            response,
            "quote",
            args=[interaction.user.display_name, message.author.display_name],
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @app_commands.command(name="inspire", description="Get a random quote.")
    @app_commands.describe(
        user="Get quotes from this user.",
    )
    @app_commands.guild_only()
    async def inspire(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ):
        await interaction.response.defer()

        image_generator = ImageGenerator(self.bot)
        if user is not None:
            quote = await self.database.get_random_quote_by_user(
                interaction.guild_id, user.id
            )
        else:
            quote = await self.database.get_random_quote(interaction.guild_id)

        image = image_generator.from_quote(quote)

        result_image = discord.File(image, "img.png")

        message_id = quote.message_id
        channel_id = quote.channel_id
        url = ""
        message = None
        if channel_id is None:
            for channel in interaction.guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                except discord.errors.NotFound:
                    continue
                except discord.errors.Forbidden:
                    pass
                if message is not None:
                    url = message.jump_url
                    await self.database.fix_quote(quote, channel.id)
                    break
        else:

            try:
                channel = await interaction.guild.get_channel(channel_id)
                if channel is not None:
                    message = await channel.fetch_message(message_id)
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                pass
            if message is not None:
                url = message.jump_url

        await interaction.followup.send(
            f"Check this Quote from <@{quote.member_id}>: {url}",
            files=[result_image],
            silent=True,
        )


async def setup(bot):
    await bot.add_cog(Quotes(bot))
