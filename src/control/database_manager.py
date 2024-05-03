import datetime

from datalayer.database import Database
from discord.ext import commands
from events.inventory_event import InventoryEvent
from items.types import ItemType

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
        "log_custom_color",
        "get_custom_color",
        "log_custom_role",
        "get_custom_role",
        "log_bully_react",
        "get_bully_react",
    ]

    PERMANENT_ITEMS = [
        ItemType.REACTION_SPAM,
        ItemType.LOTTERY_TICKET,
        ItemType.NAME_COLOR,
        ItemType.PRESTIGE_BEAN,
    ]

    def __init__(self, bot: commands.Bot, logger: BotLogger):
        self.db_season = Database(bot, logger, self.SEASON_DB_FILE)
        self.db_core = Database(bot, logger, self.CORE_DB_FILE)
        self.bot = bot

    def __getattr__(self, name):
        if name in self.CORE_METHODS:
            return getattr(self.db_core, name)

        def wrapper(*args, **kwargs):
            getattr(self.db_core, name)(*args, **kwargs)
            return getattr(self.db_season, name)(*args, **kwargs)

        return wrapper

    def migrate_permanent_items(self):
        for guild in self.bot.guilds:
            guild_item_counts = self.db_core.get_item_counts_by_guild(guild.id)
            for user_id, item_counts in guild_item_counts.items():
                current_user_items = self.db_season.get_item_counts_by_user(
                    guild.id, user_id
                )
                for item_type, count in item_counts.items():
                    if item_type in self.PERMANENT_ITEMS:
                        amount = count
                        if item_type in current_user_items:
                            amount -= current_user_items[item_type]

                        event = InventoryEvent(
                            datetime.datetime.now(),
                            guild.id,
                            user_id,
                            item_type,
                            amount,
                        )
                        self.db_season.log_event(event)
