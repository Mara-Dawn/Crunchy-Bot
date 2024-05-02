from datalayer.database import Database
from discord.ext import commands

from control.logger import BotLogger


class DatabaseManager:

    SEASON_DB_FILE = "database.sqlite"
    CORE_DB_FILE = "core.sqlite"

    CORE_METHODS = [
        "get_setting",
        "update_setting",
        "log_quote",
        "get_random_quote",
        "get_random_quote_by_user",
    ]

    def __init__(self, bot: commands.Bot, logger: BotLogger):
        self.db_season = Database(bot, logger, self.SEASON_DB_FILE)
        self.db_core = Database(bot, logger, self.CORE_DB_FILE)

    def __getattr__(self, name):
        if name in self.CORE_METHODS:
            return getattr(self.db_core, name)

        def wrapper(*args, **kwargs):
            getattr(self.db_core, name)(*args, **kwargs)
            return getattr(self.db_season, name)(*args, **kwargs)

        return wrapper
