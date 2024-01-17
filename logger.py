
import discord
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from discord.ext import commands


class BotLogger():

    def __init__(self, bot: commands.Bot, file_name: str):
        self.file_name = file_name
        self.bot = bot
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.TimedRotatingFileHandler(self.file_name,'midnight', 1, 5, 'utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def __build_log_msg(self, guild: int, message: str, cog=False) -> str:
        
        log_str = "<" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ">"
        guild_obj = self.bot.get_guild(guild)
        
        if cog:
            log_str += "[" + str(cog) + "]"
        
        if guild_obj:
            log_str += "[" + str(guild_obj.name) + ":" + str(guild) +"] "
        else:
            log_str += "[" + str(guild) + "] "

        log_str +=  str(message)

        return log_str

    def log(self, guild: int, message: str, log=True, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        #print(log_str)
        if log:
            self.logger.info("APPLICATION" + str(log_str))
    
    def debug(self, guild: int, message: str, log=True, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        #print(log_str)
        if log:
            self.logger.debug("APPLICATION" + str(log_str))