import logging
import pathlib
from logging.handlers import TimedRotatingFileHandler

from discord.ext import commands


class RecordsListHandler(logging.Handler):

    def __init__(self, records_list: list[str]):
        self.records_list = records_list
        super().__init__()

    def emit(self, record: logging.LogRecord):
        entry = self.formatter.format(record)
        self.records_list.append(entry)
        if len(self.records_list) > 10:
            self.records_list.pop(0)


class BotLogger:

    DEBUG_ENABLED = False

    def __init__(self, bot: commands.Bot, file_name: str):
        self.file_name = file_name
        self.bot = bot
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        pathlib.Path(file_name).parent.mkdir(parents=True, exist_ok=True)

        handler = TimedRotatingFileHandler(self.file_name, "midnight", 1, 5, "utf-8")
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.cache: list[str] = []
        cache_handler = RecordsListHandler(self.cache)
        formatter = logging.Formatter(
            "%(asctime)s\t%(levelname)s\t%(name)s\t %(message)s"
        )
        cache_handler.setFormatter(formatter)
        self.logger.addHandler(cache_handler)

    def __build_log_msg(self, guild: int, message: str, cog=False) -> str:
        guild_obj = self.bot.get_guild(guild)
        log_str = ""

        if guild_obj:
            log_str += "[" + str(guild_obj.name) + "]\t"
        else:
            log_str += "[" + str(guild) + "]\t"

        if cog:
            log_str += "[" + str(cog) + "] "

        log_str += str(message)

        return log_str

    def print(self, message: str) -> None:
        self.logger.info(message)

    def log(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.info(log_str)

    def error(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.error(log_str)

    def debug(self, guild: int, message: str, cog=False) -> None:
        log_str = self.__build_log_msg(guild, message, cog)
        self.logger.debug(log_str)
        if self.DEBUG_ENABLED:
            self.logger.info(log_str)
