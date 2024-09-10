import discord
from discord.ext import commands

from control.settings_manager import SettingsManager


class HelpEmbed(discord.Embed):

    def __init__(self, bot: commands.Bot):
        author_name = bot.user.display_name
        author_img = bot.user.display_avatar
        super().__init__(
            title="QuickStart Guide",
            color=discord.Colour.purple(),
            description="",
        )
        self.bot = bot
        self.set_author(name=author_name, icon_url=author_img)

    async def initialize(
        self, guild_id: int, settings_manager: SettingsManager, advanced: bool = False
    ):
        if advanced:
            self.title = "Advanced Help"

        beans_daily_min = await settings_manager.get_beans_daily_min(guild_id)
        beans_daily_max = await settings_manager.get_beans_daily_max(guild_id)
        beans_commands = []
        beans_commands.append(
            f"`/beans please` - Grants you between **{beans_daily_min}** and **{beans_daily_max}** beans. "
            "Usable once a day, resets at midnight UTC."
        )
        beans_commands.append(
            "`/beans garden` - Plant your beans, water them regularly and harvest your plants to gain even more beaans."
        )
        gamba_default = await settings_manager.get_beans_gamba_cost(guild_id)

        beans_commands.append(
            f"`/gamba` - Gamble **{gamba_default}** beans and hope for a lucky outcome."
        )
        if advanced:
            gamba_max = await settings_manager.get_beans_gamba_max(guild_id)
            beans_commands.append(
                f"`/gamba <amount>` - You may specify a custom amount, up to **{gamba_max}** beans."
            )
            beans_commands.append(
                "`/set_gamba_default <amount>` - Set a default amount to use when only using /gamba without arguments."
            )
            beans_commands.append(
                "`/beans transfer <user> <amount>` - Transfer your beans to another user."
            )
            beans_commands.append(
                "`/beans balance` - Shows your current beans balance."
            )
            beans_commands.append(
                "`/beans balance <user>` - Check in on other peoples current beans balance."
            )
            beans_commands.append(
                "`/beans lottery` - Displays information about this weeks beans lottery."
            )
            beans_commands.append(
                "`/beans prediction` - An alternative to the predictions channel. Manage your bets here."
            )
        description = "\n\n".join(beans_commands)
        description = "```Beans```\n" + description
        self.add_field(name="", value=description, inline=False)

        beans_commands = []
        beans_commands.append("`/shop` - Spend your hard earned beans in the shop.")
        beans_commands.append(
            "`/inventory` - Check your inventory and current beans balance."
        )
        if advanced:
            beans_commands.append(
                "`/catalog` - Lists all existing items and offers additional explanations."
            )
        description = "\n\n".join(beans_commands)
        description = "```Shop and Items```\n" + description
        self.add_field(name="", value=description, inline=False)

        beans_commands = []
        beans_commands.append(
            "*Fight randomly spawning enemies in the rpg channel and collect their loot!*"
        )
        beans_commands.append(
            "`/equipment` - Manage your combat equipment, skills and stats."
        )
        if advanced:
            beans_commands.append(
                "`/equipment <user>` - Inspect another users equipment."
            )
        description = "\n\n".join(beans_commands)
        description = "```RPG and Combat```\n" + description
        self.add_field(name="", value=description, inline=False)

        beans_commands = []
        beans_commands.append(
            "*All interactions are also available under **Apps** after rightclicking a user.*"
        )
        if not advanced:
            beans_commands.append("`/pet <user>` - Give someone a pet.")
            beans_commands.append("`/slap <user>` - Slap someone.")
            beans_commands.append("`/fart <user>` - fart on someone.")
        else:
            beans_commands.append(
                "*You may only modify a jail sentence once with each command.*"
            )
            pet_time = await settings_manager.get_jail_pet_time(guild_id)
            slap_time = await settings_manager.get_jail_slap_time(guild_id)
            fart_min = await settings_manager.get_jail_fart_min(guild_id)
            fart_max = await settings_manager.get_jail_fart_max(guild_id)
            beans_commands.append(
                f"`/pet <user>` - Give someone a pet. If jailed, also reduces their jailtime by **{pet_time}** minutes."
            )
            beans_commands.append(
                f"`/slap <user>` - Slap someone. If jailed, also increases their jailtime by **{slap_time}** minutes."
            )
            beans_commands.append(
                "`/fart <user>` - fart on someone. If jailed, also randomly modifies their jailtime "
                f"by **{fart_min}** to **{fart_max}** minutes."
            )

        description = "\n\n".join(beans_commands)
        description = "```Interactions```\n" + description
        self.add_field(name="", value=description, inline=False)

        if advanced:
            beans_commands = []
            beans_commands.append(
                "`/give_karma <user>` - Give someone a karma point. Resets daily at midnight UTC."
            )
            beans_commands.append(
                "`/fuck_you <user>` - Give someone a negative karma point. Resets daily at midnight UTC."
            )
            beans_commands.append("`/karma` - Check your current karma score.")
            beans_commands.append(
                "`/karma <user>` - Check the karma score of a server user."
            )
            description = "\n\n".join(beans_commands)
            description = "```Karma```\n" + description
            self.add_field(name="", value=description, inline=False)

            beans_commands = []
            beans_commands.append(
                "`/rankings` - See various leaderboards for the current beans season."
            )
            description = "\n\n".join(beans_commands)
            description = "```Leaderboards```\n" + description
            self.add_field(name="", value=description, inline=False)

            beans_commands = []
            beans_commands.append(
                "*Right click a message and save it as a quote by clicking the **Quote** option under **Apps** *"
            )
            beans_commands.append(
                "`/inspire` - Post a random motivational quote from a member of this server."
            )
            description = "\n\n".join(beans_commands)
            description = "```Quotes```\n" + description
            self.add_field(name="", value=description, inline=False)

        beans_commands = []
        if advanced:
            beans_commands.append(
                "`/personal_settings` - Various settings that only affect you.\n"
            )
        else:
            beans_commands.append(
                "`/beans help advanced` - Shows all available commands.\n"
            )
        description = "\n\n".join(beans_commands)
        description = "```More```\n" + description
        self.add_field(name="", value=description, inline=False)
