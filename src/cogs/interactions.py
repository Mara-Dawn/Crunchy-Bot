import datetime

import discord
from bot import CrunchyBot
from bot_util import Tenor
from control.controller import Controller
from control.event_manager import EventManager
from control.interaction_manager import InteractionManager
from control.item_manager import ItemManager
from control.jail_manager import JailManager
from control.logger import BotLogger
from control.settings_manager import SettingsManager
from datalayer.database import Database
from datalayer.types import UserInteraction
from discord import app_commands
from discord.ext import commands
from events.interaction_event import InteractionEvent
from items.types import ItemGroup, ItemType


class Interactions(commands.Cog):

    def __init__(self, bot: CrunchyBot):
        self.bot = bot
        self.logger: BotLogger = bot.logger
        self.database: Database = bot.database
        self.controller: Controller = bot.controller
        self.item_manager: ItemManager = self.controller.get_service(ItemManager)
        self.event_manager: EventManager = self.controller.get_service(EventManager)
        self.settings_manager: SettingsManager = self.controller.get_service(
            SettingsManager
        )
        self.interaction_manager: InteractionManager = self.controller.get_service(
            InteractionManager
        )
        self.jail_manager: JailManager = self.controller.get_service(JailManager)

        self.ctx_menu = app_commands.ContextMenu(
            name="Slap",
            callback=self.slap_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

        self.ctx_menu = app_commands.ContextMenu(
            name="Pet",
            callback=self.pet_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

        self.ctx_menu = app_commands.ContextMenu(
            name="Fart",
            callback=self.fart_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

        self.ctx_menu = app_commands.ContextMenu(
            name="Slap",
            callback=self.slap_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

        self.ctx_menu = app_commands.ContextMenu(
            name="Pet",
            callback=self.pet_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

        self.ctx_menu = app_commands.ContextMenu(
            name="Fart",
            callback=self.fart_msg_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def __check_enabled(self, interaction: discord.Interaction) -> bool:
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_jail_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__, interaction, "Jail module is currently disabled."
            )
            return False

        stun_base_duration = (
            await self.item_manager.get_item(guild_id, ItemType.BAT)
        ).value
        stunned_remaining = await self.event_manager.get_stunned_remaining(
            guild_id, interaction.user.id, stun_base_duration
        )

        if stunned_remaining > 0:
            timestamp_now = int(datetime.datetime.now().timestamp())
            remaining = int(timestamp_now + stunned_remaining)
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                f"You are currently stunned from a bat attack. Try again <t:{remaining}:R>",
            )
            return False

        return True

    @app_commands.checks.cooldown(1, 10)
    async def slap_context_menu(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        await self.__user_command_interaction(interaction, user, UserInteraction.SLAP)

    @app_commands.checks.cooldown(1, 10)
    async def pet_context_menu(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        await self.__user_command_interaction(interaction, user, UserInteraction.PET)

    @app_commands.checks.cooldown(1, 10)
    async def fart_context_menu(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        await self.__user_command_interaction(interaction, user, UserInteraction.FART)

    @app_commands.checks.cooldown(1, 10)
    async def slap_msg_context_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await self.__user_command_interaction(
            interaction, message.author, UserInteraction.SLAP
        )

    @app_commands.checks.cooldown(1, 10)
    async def pet_msg_context_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await self.__user_command_interaction(
            interaction, message.author, UserInteraction.PET
        )

    @app_commands.checks.cooldown(1, 10)
    async def fart_msg_context_menu(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await self.__user_command_interaction(
            interaction, message.author, UserInteraction.FART
        )

    def __get_response(
        self,
        interaction_type: UserInteraction,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> str:
        match interaction_type:
            case UserInteraction.SLAP:
                return f"<@{user.id}> was slapped by <@{interaction.user.id}>!"
            case UserInteraction.PET:
                return f"<@{user.id}> recieved pets from <@{interaction.user.id}>!"
            case UserInteraction.FART:
                return f"<@{user.id}> was farted on by <@{interaction.user.id}>!"

    async def __get_response_embed(
        self,
        interaction_type: UserInteraction,
    ) -> str:
        search = ""
        match interaction_type:
            case UserInteraction.SLAP:
                search = "bitchslap"
            case UserInteraction.PET:
                search = "headpats"
            case UserInteraction.FART:
                search = "fart"
        token = ""
        with open(self.bot.TENOR_TOKEN_FILE) as file:
            token = file.readline()
        g = Tenor(token)
        gif = await g.random(tag=search)
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_image(url=gif)

        return embed

    async def __user_command_interaction(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        command_type: UserInteraction,
    ):
        if not await self.__check_enabled(interaction):
            return

        command = interaction.command
        guild_id = interaction.guild_id
        invoker = interaction.user

        await interaction.response.defer()

        event = InteractionEvent(
            interaction.created_at, guild_id, command_type, invoker.id, user.id
        )
        await self.controller.dispatch_event(event)
        log_message = (
            f"{interaction.user.name} used command `{command.name}` on {user.name}."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)

        embed = await self.__get_response_embed(command_type)
        response = self.__get_response(command_type, interaction, user)

        user_items = []

        if interaction.user.id != user.id:
            user_items = (
                await self.item_manager.get_user_items_activated_by_interaction(
                    interaction.guild_id, interaction.user.id, command_type
                )
            )

        major_actions = []
        has_major_jail_actions = False

        for item in user_items:
            match item.group:
                case ItemGroup.MAJOR_ACTION:
                    major_actions.append(item)
                case ItemGroup.MAJOR_JAIL_ACTION:
                    major_actions.append(item)
                    has_major_jail_actions = True

        if len(major_actions) > 0:
            major_action_response = (
                await self.interaction_manager.handle_major_action_items(
                    major_actions, interaction.user, user
                )
            )
            response += major_action_response
            if len(major_action_response) <= 0:
                has_major_jail_actions = False

        if not has_major_jail_actions:
            response += await self.interaction_manager.user_command_interaction(
                interaction, user, command_type, user_items
            )

        await interaction.channel.send(response)
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.log(
            "init", str(self.__cog_name__) + " loaded.", cog=self.__cog_name__
        )

    # SLash Commands
    @app_commands.command(name="slap", description="Slap someone.")
    @app_commands.describe(
        user="Slap this bitch.",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def slap(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.SLAP)

    @app_commands.command(name="pet", description="Give someone a pat.")
    @app_commands.describe(
        user="Give them a pat.",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def pet(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.PET)

    @app_commands.command(name="fart", description="Fart on someone.")
    @app_commands.describe(
        user="Fart on this user.",
    )
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10)
    async def fart(self, interaction: discord.Interaction, user: discord.Member):
        await self.__user_command_interaction(interaction, user, UserInteraction.FART)


async def setup(bot):
    await bot.add_cog(Interactions(bot))
