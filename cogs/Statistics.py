import typing
import discord

from discord.ext import commands
from discord import app_commands
from typing import Dict, Literal
from BotLogger import BotLogger
from BotSettings import BotSettings
from BotUtil import BotUtil
from MaraBot import MaraBot
from datalayer.Database import Database
from datalayer.UserInteraction import UserInteraction
from events.BotEventManager import BotEventManager

class Statistics(commands.Cog):
    
    def __init__(self, bot: MaraBot):
        self.bot = bot
        
        self.logger: BotLogger = bot.logger
        self.settings: BotSettings = bot.settings
        self.database: Database = bot.database
        self.event_manager: BotEventManager = bot.event_manager
        
        
    def __get_name(self, guild_id: int, user_id: int, max_len: int = 20):
        if self.bot.get_guild(guild_id) is None or self.bot.get_guild(guild_id).get_member(user_id) is None:
            return "User not found"
        name = self.bot.get_guild(guild_id).get_member(user_id).display_name
        name = (name[:max_len] + '..') if len(name) > max_len else name
        return name
        
            
    async def __has_permission(interaction: discord.Interaction) -> bool:
        author_id = 90043934247501824
        return interaction.user.id == author_id or interaction.user.guild_permissions.administrator
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        self.logger.log("init",str(self.__cog_name__) + " loaded.", cog=self.__cog_name__)
    
    @app_commands.command(name="stats", description='See your or other peoples statistics.')
    @app_commands.describe(
        user='Leave this empty for your own statistics.',
        )
    @app_commands.guild_only()
    async def stats(self, interaction: discord.Interaction, user: typing.Optional[discord.Member] = None):
        
        await interaction.response.defer()
        
        police_img = discord.File("./img/police.png", "police.png")
        jail_img = discord.File("./img/jail.png", "jail.png")
        
        user = user if user is not None else interaction.user
        user_id = user.id
        user_statistics = self.event_manager.get_user_statistics(user_id)
        
        embed = discord.Embed(
            title=f"User Statistics for {self.__get_name(interaction.guild_id, interaction.user.id, 30)}",
            color=discord.Colour.purple(), # Pycord provides a class with default colors you can choose from
            description=f"I'm always keeping track of your degeneracy on {interaction.guild.name}, <@{interaction.user.id}>."
            
        )
        embed.add_field(name="__Interaction Count__", value="This is how much you've been spamming the server.", inline=False)
        
        embed.add_field(name="Slaps:", value=f"**{user_statistics.get_slaps_recieved()}** recieved\n**{user_statistics.get_slaps_given()}** given", inline=True)
        embed.add_field(name="Pets:", value=f"**{user_statistics.get_pets_recieved()}** recieved\n**{user_statistics.get_pets_given()}** given", inline=True)
        embed.add_field(name="Farts:", value=f"**{user_statistics.get_farts_recieved()}** recieved\n**{user_statistics.get_farts_given()}** given", inline=True)
    
        embed.add_field(name="__Top Interactions__", value="These are the people who interacted with you the most.", inline=False)
        
        top_slappers = user_statistics.get_top_slappers(5)
        top_petters = user_statistics.get_top_petters(5)
        top_farters = user_statistics.get_top_farters(5)
        
        top_slappers = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_slappers]
        top_petters = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_petters]
        top_farters = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_farters]
        
        embed.add_field(name="Top Slappers:", value="\n".join(top_slappers), inline=True)
        embed.add_field(name="Top Petters:", value="\n".join(top_petters), inline=True)
        embed.add_field(name="Top Farters:", value="\n".join(top_farters), inline=True)
        
        embed.add_field(name="", value="And the people you interacted with.", inline=False)
        
        top_slapperd = user_statistics.get_top_slapperd(5)
        top_petterd = user_statistics.get_top_petterd(5)
        top_farterd = user_statistics.get_top_farterd(5)
        
        top_slapperd = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_slapperd]
        top_petterd = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_petterd]
        top_farterd = [f'**{amount}** {self.__get_name(interaction.guild_id, user_id)}' for (user_id, amount) in top_farterd]
        
        embed.add_field(name="Top Slapped:", value="\n".join(top_slapperd), inline=True)
        embed.add_field(name="Top Petted:", value="\n".join(top_petterd), inline=True)
        embed.add_field(name="Top Farted:", value="\n".join(top_farterd), inline=True)
        
        embed.add_field(name="__Jail Stats__", value="Check how much of a bad person you are.", inline=False)
        
        embed.add_field(name="Times in jail:", value=f'**{user_statistics.get_jail_count()}**', inline=True)
        embed.add_field(name="Total jailtime:", value=BotUtil.strfdelta(user_statistics.get_jail_total(), inputtype='minutes'), inline=True)
        
        embed.add_field(name="__Timeout Stats__", value="Enter abuse statistics.", inline=False)
        
        embed.add_field(name="Times in timeout:", value=f'**{user_statistics.get_timeout_count()}**', inline=True)
        embed.add_field(name="Total timeout:", value=BotUtil.strfdelta(user_statistics.get_timeout_total(), inputtype='seconds'), inline=True)
        
        embed.add_field(name="__Bonus Stats__", value="Your other achievements.", inline=False)
        
        embed.add_field(name="Biggest Fart:", value=f'**{user_statistics.get_biggest_fart()}**', inline=True)
        embed.add_field(name="Smallest Fart:", value=f'**{user_statistics.get_smallest_fart()}**', inline=True)
        embed.add_field(name="Monkey:", value='Yes', inline=True)
        embed.add_field(name="Jailtime added to others by you:", value=BotUtil.strfdelta(user_statistics.get_total_added_others(), inputtype='minutes'), inline=True)
        embed.add_field(name="Jailtime added to self by others:", value=BotUtil.strfdelta(user_statistics.get_total_added_self(), inputtype='minutes'), inline=True)
        
        
        embed.set_author(name="Crunchy Patrol", icon_url="attachment://police.png")
        #embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text="Enjoy your stay!", icon_url="attachment://jail.png")
        
        await interaction.followup.send("", embed=embed, files=[police_img, jail_img])
    
    
    
async def setup(bot):
    await bot.add_cog(Statistics(bot))
