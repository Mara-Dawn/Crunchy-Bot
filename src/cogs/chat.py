import discord
from bot import CrunchyBot
from control.ai_manager import AIManager
from control.controller import Controller
from control.event_manager import EventManager
from control.item_manager import ItemManager
from control.logger import BotLogger
from control.role_manager import RoleManager
from control.settings_manager import SettingsManager
from datalayer.database import Database
from discord.ext import commands, tasks


class Chat(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.role_manager: RoleManager = self.controller.get_service(RoleManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.ai_manager: AIManager = self.controller.get_service(AIManager)

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.chat_timeout_check.start()
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    @tasks.loop(minutes=10)
    async def chat_timeout_check(self):
        self.logger.debug(
            "sys", "ai chatlog decay check task started", cog=self.__cog_name__
        )
        count = self.ai_manager.clean_up_logs(1)

        if count > 0:
            self.logger.log(
                "sys", f"Cleaned up {count} old ai chat logs.", cog=self.__cog_name__
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        if message.author.bot:
            return

        if not message.guild:
            return

        if not self.bot.user.mentioned_in(message):
            return

        beans_channels = self.settings_manager.get_beans_channels(message.guild.id)
        jail_channels = self.settings_manager.get_jail_channels(message.guild.id)
        if (
            message.channel.id not in beans_channels
            and message.channel.id not in jail_channels
        ):
            return

        await self.ai_manager.respond(message)


async def setup(bot):
    await bot.add_cog(Chat(bot))
