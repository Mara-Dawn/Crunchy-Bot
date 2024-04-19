import discord
from bot import CrunchyBot
from bot_util import BotUtil
from datalayer.stats import UserStats


class StatisticsEmbed(discord.Embed):

    def __init__(
        self,
        bot: CrunchyBot,
        interaction: discord.Interaction,
        user: discord.Member,
        user_statistics: UserStats,
    ):
        super().__init__(
            title=f"User Statistics for {BotUtil.get_name(bot, interaction.guild_id, user.id, 30)}",
            color=discord.Colour.purple(),
            description=f"I'm always keeping track of your degeneracy on {interaction.guild.name}, <@{user.id}>.",
        )
        self.add_field(
            name="__Interaction Count__",
            value="This is how much you've been spamming the server.",
            inline=False,
        )

        self.add_field(
            name="Slaps:",
            value=f"**{user_statistics.get_slaps_recieved()}** recieved\n**{user_statistics.get_slaps_given()}** given",
            inline=True,
        )
        self.add_field(
            name="Pets:",
            value=f"**{user_statistics.get_pets_recieved()}** recieved\n**{user_statistics.get_pets_given()}** given",
            inline=True,
        )
        self.add_field(
            name="Farts:",
            value=f"**{user_statistics.get_farts_recieved()}** recieved\n**{user_statistics.get_farts_given()}** given",
            inline=True,
        )

        self.add_field(
            name="__Top Interactions__",
            value="These are the people who interacted with you the most.",
            inline=False,
        )

        top_slappers = user_statistics.get_top_slappers(5)
        top_petters = user_statistics.get_top_petters(5)
        top_farters = user_statistics.get_top_farters(5)

        top_slappers = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_slappers
        ]
        top_petters = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_petters
        ]
        top_farters = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_farters
        ]

        self.add_field(name="Top Slappers:", value="\n".join(top_slappers), inline=True)
        self.add_field(name="Top Petters:", value="\n".join(top_petters), inline=True)
        self.add_field(name="Top Farters:", value="\n".join(top_farters), inline=True)

        top_slapperd = user_statistics.get_top_slapperd(5)
        top_petterd = user_statistics.get_top_petterd(5)
        top_farterd = user_statistics.get_top_farterd(5)

        top_slapperd = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_slapperd
        ]
        top_petterd = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_petterd
        ]
        top_farterd = [
            f"**{amount}** {BotUtil.get_name(bot, interaction.guild_id, user_id)}"
            for (user_id, amount) in top_farterd
        ]

        self.add_field(name="Top Slapped:", value="\n".join(top_slapperd), inline=True)
        self.add_field(name="Top Petted:", value="\n".join(top_petterd), inline=True)
        self.add_field(name="Top Farted:", value="\n".join(top_farterd), inline=True)

        self.add_field(
            name="__Jail Stats__",
            value="Check how much of a bad person you are. Increases and reductions taken from interactions (/slap etc) in jail.",
            inline=False,
        )

        self.add_field(
            name="Times in jail:",
            value=f"**{user_statistics.get_jail_count()}**",
            inline=True,
        )
        self.add_field(
            name="inc. (to others):",
            value=BotUtil.strfdelta(
                user_statistics.get_total_added_to_others(), inputtype="minutes"
            ),
            inline=True,
        )
        self.add_field(
            name="red. (to others):",
            value=BotUtil.strfdelta(
                user_statistics.get_total_reduced_from_others(), inputtype="minutes"
            ),
            inline=True,
        )
        self.add_field(
            name="Total jailtime:",
            value=BotUtil.strfdelta(
                user_statistics.get_jail_total(), inputtype="minutes"
            ),
            inline=True,
        )
        self.add_field(
            name="inc. (from others):",
            value=BotUtil.strfdelta(
                user_statistics.get_total_added_to_self(), inputtype="minutes"
            ),
            inline=True,
        )
        self.add_field(
            name="red. (from others):",
            value=BotUtil.strfdelta(
                user_statistics.get_total_reduced_from_self(), inputtype="minutes"
            ),
            inline=True,
        )

        self.add_field(
            name="__Timeout Stats__", value="Enter abuse statistics.", inline=False
        )

        self.add_field(
            name="Times in timeout:",
            value=f"**{user_statistics.get_timeout_count()}**",
            inline=True,
        )
        self.add_field(
            name="Total timeout:",
            value=BotUtil.strfdelta(
                user_statistics.get_timeout_total(), inputtype="seconds"
            ),
            inline=True,
        )

        self.add_field(
            name="__Bonus Stats__", value="Your other achievements.", inline=False
        )

        self.add_field(
            name="Biggest Fart:",
            value=f"**{user_statistics.get_biggest_fart()}**",
            inline=True,
        )
        self.add_field(
            name="Smallest Fart:",
            value=f"**{user_statistics.get_smallest_fart()}**",
            inline=True,
        )
        self.add_field(
            name="Spam Score:",
            value=f"**{user_statistics.get_spam_score()}**",
            inline=True,
        )

        self.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
        self.set_thumbnail(url=user.avatar.url)
        self.set_footer(text="Enjoy your stay!", icon_url="attachment://jail.png")
