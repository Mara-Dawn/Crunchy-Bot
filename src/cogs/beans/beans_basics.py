import datetime
import random
import typing

import discord
from control.settings_manager import SettingsManager
from discord import app_commands
from discord.ext import commands
from events.beans_event import BeansEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType
from items.types import ItemType
from view.settings_modal import SettingsModal

from cogs.beans.beans_group import BeansGroup


class BeansBasics(BeansGroup):

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __check_enabled(self, interaction: discord.Interaction) -> bool:
        guild_id = interaction.guild_id

        if not await self.settings_manager.get_beans_enabled(guild_id):
            await self.bot.command_response(
                self.__cog_name__, interaction, "Beans module is currently disabled."
            )
            return False

        if (
            interaction.channel_id
            not in await self.settings_manager.get_beans_channels(guild_id)
        ):
            await self.bot.command_response(
                self.__cog_name__,
                interaction,
                "Beans commands cannot be used in this channel.",
            )
            return False

        return True

    @commands.Cog.listener("on_ready")
    async def on_ready_beansbasics(self) -> None:
        self.logger.log("init", "BeansBasics loaded.", cog=self.__cog_name__)

    @app_commands.command(name="please", description="Your daily dose of beans.")
    @app_commands.guild_only()
    async def please(self, interaction: discord.Interaction) -> None:
        if not await self.__check_enabled(interaction):
            return

        guild_id = interaction.guild_id
        user_id = interaction.user.id

        last_daily_beans_event = await self.database.get_last_beans_event(
            guild_id, user_id, BeansEventType.DAILY
        )

        if last_daily_beans_event is not None:

            current_date = datetime.datetime.now().date()
            last_daily_beans_date = last_daily_beans_event.datetime.date()

            if current_date == last_daily_beans_date:
                await self.bot.command_response(
                    self.__cog_name__,
                    interaction,
                    "You already got your daily beans, dummy! Try again tomorrow.",
                    ephemeral=False,
                )
                return

        beans_daily_min = await self.settings_manager.get_beans_daily_min(guild_id)
        beans_daily_max = await self.settings_manager.get_beans_daily_max(guild_id)

        amount = random.randint(beans_daily_min, beans_daily_max)

        event = BeansEvent(
            datetime.datetime.now(), guild_id, BeansEventType.DAILY, user_id, amount
        )
        await self.controller.dispatch_event(event)

        await self.bot.command_response(
            module=self.__cog_name__,
            interaction=interaction,
            message=f"<@{user_id}> got their daily dose of `🅱️{amount}` beans.",
            args=[amount],
            ephemeral=False,
        )

    @app_commands.command(name="balance", description="Your current bean balance.")
    @app_commands.describe(user="Optional, check this users bean balance.")
    @app_commands.guild_only()
    async def balance(
        self,
        interaction: discord.Interaction,
        user: discord.Member | None = None,
    ) -> None:
        if not await self.__check_enabled(interaction):
            return

        user = user if user is not None else interaction.user
        user_id = user.id

        guild_id = interaction.guild_id

        current_balance = await self.database.get_member_beans(guild_id, user_id)

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"<@{user_id}> currently has `🅱️{current_balance}` beans.",
            args=[user.display_name],
            ephemeral=False,
        )

    @app_commands.command(
        name="grant",
        description="Give or remove beans from specific users. (Admin only)",
    )
    @app_commands.describe(
        user="User to give beans to.", amount="Amount of beans, can be negative."
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def grant(
        self, interaction: discord.Interaction, user: discord.Member, amount: int
    ) -> None:
        guild_id = interaction.guild_id

        event = BeansEvent(
            timestamp=datetime.datetime.now(),
            guild_id=guild_id,
            beans_event_type=BeansEventType.BALANCE_CHANGE,
            member_id=user.id,
            value=amount,
        )
        await self.controller.dispatch_event(event)

        response = f"`🅱️{abs(amount)}` beans were "
        if amount >= 0:
            response += "added to "
        else:
            response += "subtracted from "

        response += f"<@{user.id}>'s bean balance by <@{interaction.user.id}>"

        await self.bot.command_response(
            module=self.__cog_name__,
            interaction=interaction,
            message=response,
            args=[user.display_name, amount],
            ephemeral=False,
        )

    @app_commands.command(
        name="transfer", description="Transfer your beans to other users."
    )
    @app_commands.describe(user="User to transfer beans to.", amount="Amount of beans.")
    @app_commands.guild_only()
    async def transfer(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: app_commands.Range[int, 1],
    ) -> None:
        await interaction.response.defer()

        guild_id = interaction.guild_id
        user_id = interaction.user.id

        current_balance = await self.database.get_member_beans(guild_id, user_id)

        if current_balance < amount:
            await self.bot.command_response(
                module=self.__cog_name__,
                interaction=interaction,
                message="You dont have that many beans, idiot.",
                ephemeral=False,
            )
            return
        now = datetime.datetime.now()

        event = BeansEvent(
            now, guild_id, BeansEventType.USER_TRANSFER, interaction.user.id, -amount
        )
        await self.controller.dispatch_event(event)

        event = BeansEvent(now, guild_id, BeansEventType.USER_TRANSFER, user.id, amount)
        await self.controller.dispatch_event(event)

        response = f"`🅱️{abs(amount)}` beans were transferred from <@{interaction.user.id}> to <@{user.id}>."

        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            response,
            args=[interaction.user.display_name, user.display_name, amount],
            ephemeral=False,
        )

    @app_commands.command(
        name="award_prestige",
        description="Award prestige beans based on current seasons high score.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def award_prestige(self, interaction: discord.Interaction) -> None:
        author_id = 90043934247501824
        await interaction.response.defer()
        if interaction.user.id != author_id:
            raise app_commands.MissingPermissions

        guild_id = interaction.guild_id

        rankings = await self.database.get_guild_beans_rankings(guild_id)
        lootbox_purchases = await self.database.get_lootbox_purchases_by_guild(
            guild_id,
            datetime.datetime(year=2024, month=4, day=22, hour=14).timestamp(),
        )
        loot_box_item = await self.item_manager.get_item(guild_id, ItemType.LOOTBOX)

        for user_id, amount in lootbox_purchases.items():
            if user_id in rankings:
                rankings[user_id] -= amount * loot_box_item.cost

        rankings = sorted(rankings.items(), key=lambda item: item[1], reverse=True)

        for rank, (user_id, score) in enumerate(rankings):
            author = self.bot.get_user(user_id)
            if author is not None and author.id != self.bot.user.id:
                amount = int(score / 10000)

                event = InventoryEvent(
                    datetime.datetime.now(),
                    guild_id,
                    author.id,
                    ItemType.PRESTIGE_BEAN,
                    amount,
                )
                await self.controller.dispatch_event(event)

                message = f"Congratulations, the current Beans Season has concluded and your final rank is: 🎉**Rank {rank+1}.**🎉\n"
                if rank < 10:
                    message += "You made it to the top 10, which means you get to choose additional rewards! Check out the Beans Info channel for more Information."
                message += f"```python\nHigh Score: 🅱️{score}\nReward: 1 Prestige Bean per 10k\n-----------------------\nPayout: {amount} x Prestige Bean```"
                await author.send(message)

        output = "Action complete."
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @app_commands.command(
        name="migrate_permanent_items",
        description="Migrates everyones permanent items to the new season.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def migrate_permanent_items(self, interaction: discord.Interaction) -> None:
        author_id = 90043934247501824
        if interaction.user.id != author_id:
            raise app_commands.MissingPermissions

        await self.database.migrate_permanent_items(self.item_manager)

        output = "Migration complete."
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @app_commands.command(
        name="settings",
        description="Overview of all beans related settings and their current value.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def get_settings(self, interaction: discord.Interaction) -> None:
        output = await self.settings_manager.get_settings_string(
            interaction.guild_id, SettingsManager.BEANS_SUBSETTINGS_KEY
        )
        await self.bot.command_response(self.__cog_name__, interaction, output)

    @app_commands.command(
        name="toggle", description="Enable or disable the entire beans module."
    )
    @app_commands.describe(enabled="Turns the beans module on or off.")
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def set_toggle(
        self, interaction: discord.Interaction, enabled: typing.Literal["on", "off"]
    ) -> None:
        await self.settings_manager.set_beans_enabled(
            interaction.guild_id, enabled == "on"
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Beans module was turned {enabled}.",
            args=[enabled],
        )

    @app_commands.command(
        name="daily_setup",
        description="Opens a dialog to edit various daily and bonus beans settings.",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def daily_setup(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        modal = SettingsModal(
            self.bot,
            self.settings_manager,
            self.__cog_name__,
            interaction.command.name,
            "Settings for Daily Beans related Features",
        )

        await modal.add_field(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_DAILY_MIN_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_DAILY_MAX_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_BONUS_CARD_AMOUNT_10_KEY,
            int,
        )
        await modal.add_field(
            guild_id,
            SettingsManager.BEANS_SUBSETTINGS_KEY,
            SettingsManager.BEANS_BONUS_CARD_AMOUNT_25_KEY,
            int,
        )

        modal.add_constraint(
            [SettingsManager.BEANS_DAILY_MIN_KEY, SettingsManager.BEANS_DAILY_MAX_KEY],
            lambda a, b: a <= b,
            "Beans minimum must be smaller than Beans maximum.",
        )

        await interaction.response.send_modal(modal)

    @app_commands.command(
        name="add_channel", description="Enable beans commands for a channel."
    )
    @app_commands.describe(channel="The beans channel.")
    @app_commands.check(__has_permission)
    async def add_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.add_beans_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {channel.name} to beans channels.",
            args=[channel.name],
        )

    @app_commands.command(
        name="remove_channel", description="Disable beans commands for a channel."
    )
    @app_commands.describe(channel="Removes this channel from the beans channels.")
    @app_commands.check(__has_permission)
    async def remove_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.remove_beans_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {channel.name} from beans channels.",
            args=[channel.name],
        )

    @app_commands.command(
        name="add_mod_channel",
        description="Enable this channel to recieve mod notifications.",
    )
    @app_commands.describe(channel="The new mod channel.")
    @app_commands.check(__has_permission)
    async def add_mod_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.add_mod_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {channel.name} to mod channels.",
            args=[channel.name],
        )

    @app_commands.command(
        name="remove_mod_channel",
        description="Disable mod notifications for a channel.",
    )
    @app_commands.describe(
        channel="Removes this channel from recieving mod notifications."
    )
    @app_commands.check(__has_permission)
    async def remove_mod_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.remove_mod_channel(interaction.guild_id, channel.id)
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {channel.name} from mod channels.",
            args=[channel.name],
        )

    @app_commands.command(
        name="add_notification_channel",
        description="Enable this channel to recieve beans notifications.",
    )
    @app_commands.describe(channel="The new beans notification channel.")
    @app_commands.check(__has_permission)
    async def add_notification_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.add_beans_notification_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Added {channel.name} to beans notification channels.",
            args=[channel.name],
        )

    @app_commands.command(
        name="remove_notification_channel",
        description="Disable beans notifications for a channel.",
    )
    @app_commands.describe(
        channel="Removes this channel from recieving beans notifications."
    )
    @app_commands.check(__has_permission)
    async def remove_notification_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        await self.settings_manager.remove_beans_notification_channel(
            interaction.guild_id, channel.id
        )
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"Removed {channel.name} from beans notification channels.",
            args=[channel.name],
        )


async def setup(bot):
    await bot.add_cog(BeansBasics(bot))
