import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from cogs.beans.beans_group import BeansGroup
from control.settings_manager import SettingsManager
from items.types import ItemType
from view.inventory_embed import InventoryEmbed
from view.shop_embed import ShopEmbed
from view.shop_view import ShopView


class Predictions(BeansGroup):

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    def __has_mod_permission(self, interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        roles = self.settings_manager.get_predictions_mod_roles(interaction.guild_id)
        is_mod = (
            len(set([x.id for x in interaction.user.roles]).intersection(roles)) > 0
        )
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
            or is_mod
        )

    async def __check_enabled(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id

        if not self.settings_manager.get_predictions_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans predictions module is currently disabled.",
            )
            return False

        if interaction.channel_id not in self.settings_manager.get_beans_channels(
            guild_id
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Prediction commands cannot be used in this channel.",
            )
            return False

        stun_base_duration = self.item_manager.get_item(guild_id, ItemType.BAT).value
        stunned_remaining = self.event_manager.get_stunned_remaining(
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

    @commands.Cog.listener("on_ready")
    async def on_ready_prediction(self) -> None:
        self.logger.log("init", "Predictions loaded.", cog=self.__cog_name__)

    @app_commands.command(
        name="predictions", description="Bet your beans on various predictions."
    )
    @app_commands.guild_only()
    async def predictions(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        shop_img = discord.File("./img/shop.png", "shop.png")
        police_img = discord.File("./img/police.png", "police.png")
        items = self.item_manager.get_items(interaction.guild_id)

        items = sorted(items, key=lambda x: (x.shop_category.value, x.cost))

        user_balance = self.database.get_member_beans(
            interaction.guild.id, interaction.user.id
        )
        user_items = self.database.get_item_counts_by_user(
            interaction.guild.id, interaction.user.id
        )
        embed = ShopEmbed(interaction.guild.name, interaction.user.id, items)

        view = ShopView(self.controller, interaction, items)

        message = await interaction.followup.send(
            "", embed=embed, view=view, files=[shop_img, police_img], ephemeral=True
        )
        view.set_message(message)
        await view.refresh_ui(user_balance=user_balance, user_items=user_items)

    @app_commands.command(
        name="prediction_moderation",
        description="Prediction moderation interface.",
    )
    @app_commands.guild_only()
    async def prediction_moderation(self, interaction: discord.Interaction):
        if not await self.__check_enabled(interaction):
            return

        if not await self.__has_mod_permission(interaction):
            raise app_commands.MissingPermissions([])

        log_message = (
            f"{interaction.user.name} used command `{interaction.command.name}`."
        )
        self.logger.log(interaction.guild_id, log_message, cog=self.__cog_name__)
        await interaction.response.defer(ephemeral=True)

        police_img = discord.File("./img/police.png", "police.png")

        member_id = interaction.user.id
        guild_id = interaction.guild_id

        inventory = self.item_manager.get_user_inventory(guild_id, member_id)
        embed = InventoryEmbed(inventory)

        await interaction.followup.send("", embed=embed, files=[police_img])

    group = app_commands.Group(
        name="predictions", description="Subcommands for the Beans Predictions module."
    )

    @group.command(
        name="settings",
        description="Overview of all beans prediction related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction):
        output = self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.PREDICTIONS_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @group.command(
        name="toggle",
        description="Enable or disable the entire beans prediction module.",
    )
    @app_commands.describe(enabled="Turns the beans prediction module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: Literal["on", "off"]
    ):
        self.settings_manager.set_predictions_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Beans prediction module was turned {enabled}.",
            args=[enabled],
        )

    @group.command(
        name="add_mod_role",
        description="Add prediction moderation privileges to a role.",
    )
    @app_commands.describe(role="This role will be allowed to moderate predictions.")
    @app_commands.check(__has_permission)
    async def add_mod_role(self, interaction: discord.Interaction, role: discord.Role):
        self.settings_manager.add_predictions_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {role.name} to prediction moderators.",
            args=[role.name],
        )

    @group.command(
        name="remove_mod_role",
        description="Remove prediction moderation privileges from a role.",
    )
    @app_commands.describe(role="Removes role from prediction moderators.")
    @app_commands.check(__has_permission)
    async def remove_mod_role(
        self, interaction: discord.Interaction, role: discord.Role
    ):
        self.settings_manager.remove_predictions_mod_role(interaction.guild_id, role.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {role.name} from prediction moderators.",
            args=[role.name],
        )


async def setup(bot):
    await bot.add_cog(Predictions(bot))
