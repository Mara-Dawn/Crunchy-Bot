
import discord
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

class _ColourFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.
    # yoinked from https://github.com/Rapptz/discord.py/blob/master/discord/utils.py#L1262

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output

class BotLogger():

    def __init__(self, bot: discord.Bot, file_name: str):
        self.file_name = file_name
        self.bot = bot
        
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)
        handler = TimedRotatingFileHandler(self.file_name,'midnight', 1, 5, 'utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)
        
        handler = logging.StreamHandler()
        formatter = _ColourFormatter()
        handler.setFormatter(formatter)
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