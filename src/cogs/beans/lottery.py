import datetime
import secrets
import traceback

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot_util import BotUtil
from cogs.beans.beans_group import BeansGroup
from error import ErrorHandler
from events.beans_event import BeansEvent
from events.inventory_event import InventoryEvent
from events.types import BeansEventType
from items.types import ItemType


class Lottery(BeansGroup):

    @staticmethod
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return (
            interaction.user.id == author_id
            or interaction.user.guild_permissions.administrator
        )

    async def __beans_role_check(self, interaction: discord.Interaction) -> bool:
        member = interaction.user
        guild_id = interaction.guild_id

        beans_role = await self.settings_manager.get_beans_role(guild_id)
        if beans_role is None:
            return True
        if beans_role in [role.id for role in member.roles]:
            return True

        role_name = interaction.guild.get_role(beans_role).name
        await self.bot.command_response(
            self.__cog_name__,
            interaction,
            f"You can only use this command if you have the role `{role_name}`.",
        )
        return False

    async def __draw_lottery(self, guild: discord.Guild) -> None:
        guild_id = guild.id
        base_pot = await self.settings_manager.get_beans_lottery_base_amount(guild_id)
        bean_channels = await self.settings_manager.get_beans_channels(guild_id)
        allowed_mentions = discord.AllowedMentions(roles=True)
        lottery_data = await self.database.get_lottery_data(guild_id)
        total_pot = base_pot
        ticket_pool = []
        participants = len(lottery_data)
        item = await self.item_manager.get_item(guild_id, ItemType.LOTTERY_TICKET)

        for user_id, count in lottery_data.items():
            for _ in range(count):
                ticket_pool.append(user_id)
            total_pot += item.cost * count

        lottery_role: discord.Role = await self.role_manager.get_lottery_role(guild)

        response = f"# Weekly Crunchy Beans Lottery \nThis weeks <@&{lottery_role.id}> has `{participants}` participants with a total pot of  `🅱️{total_pot}` beans."

        if len(ticket_pool) == 0:
            self.logger.log(
                guild_id, "Lottery had no participants.", cog=self.__cog_name__
            )
            response += "\n\nNo winner this week due to lack of participation."
            for channel_id in bean_channels:
                channel = guild.get_channel(channel_id)
                if channel is None:
                    continue
                await channel.send(response, allowed_mentions=allowed_mentions)
            return

        winner = secrets.choice(ticket_pool)

        event = BeansEvent(
            datetime.datetime.now(),
            guild_id,
            BeansEventType.LOTTERY_PAYOUT,
            winner,
            total_pot,
        )
        await self.controller.dispatch_event(event)

        response += f"\n\n**The lucky winner is:**\n🎉 <@{winner}> 🎉\n **Congratulations, the `🅱️{total_pot}` beans were tansferred to your account!**\n\n Thank you for playing 😊"

        self.logger.log(
            guild_id,
            f"Lottery draw complete. Winner is {BotUtil.get_name(self.bot, guild_id, winner)} with a pot of {total_pot}",
            cog=self.__cog_name__,
        )

        for channel_id in bean_channels:
            channel = guild.get_channel(channel_id)
            if channel is None:
                continue
            await channel.send(response, allowed_mentions=allowed_mentions)

        for user_id, count in lottery_data.items():
            event = InventoryEvent(
                datetime.datetime.now(), guild_id, user_id, item.type, -count
            )
            await self.controller.dispatch_event(event)

    @commands.Cog.listener("on_ready")
    async def on_ready_lottery(self) -> None:
        self.lottery_task.start()
        self.logger.log("init", "Lottery loaded.", cog=self.__cog_name__)

    @tasks.loop(time=datetime.time(hour=12, tzinfo=datetime.UTC))
    async def lottery_task(self) -> None:
        self.logger.log("sys", "Lottery task started.", cog=self.__cog_name__)

        try:
            if datetime.datetime.today().weekday() != 5:
                # only on saturdays
                self.logger.log(
                    "sys", "Not saturday so skipping.", cog=self.__cog_name__
                )
                return

            for guild in self.bot.guilds:
                if not await self.settings_manager.get_beans_enabled(guild.id):
                    self.logger.log(
                        "sys", "Beans module disabled.", cog=self.__cog_name__
                    )
                    return

                await self.__draw_lottery(guild)
        except Exception as e:
            print(traceback.format_exc())
            error_handler = ErrorHandler(self.bot)
            await error_handler.post_error(e)

    @app_commands.command(
        name="lottery",
        description="Check the current pot for this weeks beans lottery.",
    )
    @app_commands.guild_only()
    async def lottery(self, interaction: discord.Interaction):
        if not await self.__beans_role_check(interaction):
            return
        guild_id = interaction.guild_id
        base_pot = await self.settings_manager.get_beans_lottery_base_amount(guild_id)

        lottery_data = await self.database.get_lottery_data(guild_id)
        total_pot = base_pot
        participants = len(lottery_data)
        item = await self.item_manager.get_item(guild_id, ItemType.LOTTERY_TICKET)

        for count in lottery_data.values():
            total_pot += item.cost * count

        today = datetime.datetime.now(datetime.UTC)
        saturday = today + datetime.timedelta((5 - today.weekday()) % 7)
        if today.date() == saturday.date() and today.time().hour >= 12:
            saturday += datetime.timedelta(weeks=1)

        next_draw = datetime.datetime(
            year=saturday.year,
            month=saturday.month,
            day=saturday.day,
            hour=12,
            tzinfo=datetime.UTC,
        )

        response = f"This weeks lottery has `{participants}` participants with a total pot of  `🅱️{total_pot}` beans."
        response += f"\nThe draw happens every Saturday noon at 12 PM UTC. Next draw <t:{int(next_draw.timestamp())}:R>."

        if participants > 0:
            participant_list = ", ".join(
                [
                    BotUtil.get_name(self.bot, guild_id, k, max_len=50) + f"[{v}]"
                    for k, v in lottery_data.items()
                ]
            )
            participant_list = "```Participants: " + participant_list + "```"
            response += participant_list

        await self.bot.command_response(
            self.__cog_name__, interaction, response, ephemeral=False
        )

    @app_commands.command(
        name="lottery_draw",
        description="Manually draw the winner of this weeks bean lottery. (Admin only)",
    )
    @app_commands.check(__has_permission)
    @app_commands.guild_only()
    async def lottery_draw(self, interaction: discord.Interaction):
        await self.__draw_lottery(interaction.guild)
        await self.bot.command_response(
            self.__cog_name__, interaction, "Lottery was drawn."
        )


async def setup(bot):
    await bot.add_cog(Lottery(bot))
