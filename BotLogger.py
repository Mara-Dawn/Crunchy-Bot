
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
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.TimedRotatingFileHandler(self.file_name,'midnight', 1, 5, 'utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    def __build_log_msg(self, guild: int, message: str, cog=False) -> str:
        
        guild_obj = self.bot.get_guild(guild)
        log_str = "";
        if cog:
            log_str += "[" + str(cog) + "]"
        
        if guild_obj:
            log_str += "[" + str(guild_obj.name) + "] "
        else:
            log_str += "[" + str(guild) + "] "

        log_str +=  str(message)

        return log_str

    def log(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.info(log_str)
    
    def error(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.error(log_str)
    
    def debug(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.debug(log_str)