import datetime
import inspect

import discord
from datalayer.database import Database
from datalayer.jail import UserJail
from datalayer.lootbox import LootBox
from datalayer.prediction import Prediction
from datalayer.prediction_stats import PredictionStats
from datalayer.quote import Quote
from datalayer.types import PredictionState, UserInteraction
from discord.ext import commands
from events.bat_event import BatEvent
from events.beans_event import BeansEvent
from events.bot_event import BotEvent
from events.interaction_event import InteractionEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.spam_event import SpamEvent
from events.timeout_event import TimeoutEvent
from events.types import BeansEventType
from items.types import ItemState, ItemType
from view.types import EmojiType

from control.item_manager import ItemManager
from control.logger import BotLogger


class DatabaseManager:

    SEASON_DB_FILE = "season.sqlite"
    CORE_DB_FILE = "database.sqlite"

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
    ]

    def __init__(self, bot: commands.Bot, logger: BotLogger):
        self.db_season = Database(bot, logger, self.SEASON_DB_FILE)
        self.db_core = Database(bot, logger, self.CORE_DB_FILE)
        self.bot = bot

    async def init(self):
        await self.db_core.create_tables(self.CORE_DB_FILE)
        await self.db_season.create_tables(self.SEASON_DB_FILE)

    async def migrate_permanent_items(self, item_manager: ItemManager):
        for guild in self.bot.guilds:
            guild_item_counts = await self.db_core.get_item_counts_by_guild(guild.id)
            for user_id, item_counts in guild_item_counts.items():
                current_user_items = await self.db_season.get_item_counts_by_user(
                    guild.id, user_id
                )
                for item_type, count in item_counts.items():

                    item = item_manager.get_item(guild.id, item_type)

                    if item_type in self.PERMANENT_ITEMS or item.permanent:
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
                        await self.db_season.log_event(event)

    def __core_only(self):
        name = inspect.getouterframes(inspect.currentframe())[1][3]
        return name in self.CORE_METHODS

    async def get_setting(self, guild_id: int, module: str, key: str):
        result = await self.db_core.get_setting(guild_id, module, key)
        if not self.__core_only():
            result = await self.db_season.get_setting(guild_id, module, key)
        return result

    async def update_setting(self, guild_id: int, module: str, key: str, value):
        result = await self.db_core.update_setting(guild_id, module, key, value)
        if not self.__core_only():
            result = await self.db_season.update_setting(guild_id, module, key, value)
        return result

    async def log_event(self, event: BotEvent) -> int:
        result = await self.db_core.log_event(event)
        if not self.__core_only():
            result = await self.db_season.log_event(event)
        return result

    async def log_quote(self, quote: Quote) -> int:
        result = await self.db_core.log_quote(quote)
        if not self.__core_only():
            result = await self.db_season.log_quote(quote)
        return result

    async def log_lootbox(self, loot_box: LootBox) -> int:
        result = await self.db_core.log_lootbox(loot_box)
        if not self.__core_only():
            result = await self.db_season.log_lootbox(loot_box)
        return result

    async def log_item_state(
        self,
        guild_id: int,
        user_id: int,
        item_type: ItemType,
        item_state: ItemState,
    ) -> int:
        result = await self.db_core.log_item_state(
            guild_id, user_id, item_type, item_state
        )
        if not self.__core_only():
            result = await self.db_season.log_item_state(
                guild_id, user_id, item_type, item_state
            )
        return result

    async def get_user_item_states(
        self, guild_id: int, user_id: int
    ) -> dict[ItemType, ItemState]:
        result = await self.db_core.get_user_item_states(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_user_item_states(guild_id, user_id)
        return result

    async def log_bully_react(
        self,
        guild_id: int,
        user_id: int,
        target_id: int,
        emoji_type: EmojiType,
        emoji: discord.Emoji | str,
    ) -> int:
        result = await self.db_core.log_bully_react(
            guild_id, user_id, target_id, emoji_type, emoji
        )
        if not self.__core_only():
            result = await self.db_season.log_bully_react(
                guild_id, user_id, target_id, emoji_type, emoji
            )
        return result

    async def get_bully_react(
        self, guild_id: int, user_id: int
    ) -> tuple[int, discord.Emoji | str]:
        result = result = await self.db_core.get_bully_react(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_bully_react(guild_id, user_id)
        return result

    async def log_custom_color(self, guild_id: int, user_id: int, color: str) -> int:
        result = await self.db_core.log_custom_color(guild_id, user_id, color)
        if not self.__core_only():
            result = await self.db_season.log_custom_color(guild_id, user_id, color)
        return result

    async def get_custom_color(self, guild_id: int, user_id: int) -> str:
        result = await self.db_core.get_custom_color(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_custom_color(guild_id, user_id)
        return result

    async def log_custom_role(self, guild_id: int, user_id: int, role_id: int) -> int:
        result = await self.db_core.log_custom_role(guild_id, user_id, role_id)
        if not self.__core_only():
            result = await self.db_season.log_custom_role(guild_id, user_id, role_id)
        return result

    async def get_custom_role(self, guild_id: int, user_id: int) -> int:
        result = await self.db_core.get_custom_role(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_custom_role(guild_id, user_id)
        return result

    async def log_prediction(self, prediction: Prediction) -> int:
        result = await self.db_core.log_prediction(prediction)
        if not self.__core_only():
            result = await self.db_season.log_prediction(prediction)
        return result

    async def update_prediction(self, prediction: Prediction) -> int:
        result = await self.db_core.update_prediction(prediction)
        if not self.__core_only():
            result = await self.db_season.update_prediction(prediction)
        return result

    async def clear_prediction_overview_messages(self, channel_id: int) -> int:
        result = await self.db_core.clear_prediction_overview_messages(channel_id)
        if not self.__core_only():
            result = await self.db_season.clear_prediction_overview_messages(channel_id)
        return result

    async def add_prediction_overview_message(
        self, prediction_id: int, message_id: int, channel_id: int
    ) -> int:
        result = await self.db_core.add_prediction_overview_message(
            prediction_id, message_id, channel_id
        )
        if not self.__core_only():
            result = await self.db_season.add_prediction_overview_message(
                prediction_id, message_id, channel_id
            )
        return result

    async def get_prediction_overview_message(
        self, prediction_id: int, channel_id: int
    ) -> int:
        result = await self.db_core.get_prediction_overview_message(
            prediction_id, channel_id
        )
        if not self.__core_only():
            result = await self.db_season.get_prediction_overview_message(
                prediction_id, channel_id
            )
        return result

    async def fix_quote(self, quote: Quote, channel_id: int) -> int:
        result = await self.db_core.fix_quote(quote, channel_id)
        if not self.__core_only():
            result = await self.db_season.fix_quote(quote, channel_id)
        return result

    async def increment_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        result = await self.db_core.increment_timeout_tracker(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.increment_timeout_tracker(guild_id, user_id)
        return result

    async def reset_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        result = await self.db_core.reset_timeout_tracker(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.reset_timeout_tracker(guild_id, user_id)
        return result

    async def get_timeout_tracker_count(self, guild_id: int, user_id: int) -> int:
        result = await self.db_core.get_timeout_tracker_count(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_timeout_tracker_count(guild_id, user_id)
        return result

    async def log_jail_sentence(self, jail: UserJail) -> UserJail:
        result = await self.db_core.log_jail_sentence(jail)
        if not self.__core_only():
            result = await self.db_season.log_jail_sentence(jail)
        return result

    async def log_jail_release(self, jail_id: int, released_on: int) -> int:
        result = await self.db_core.log_jail_release(jail_id, released_on)
        if not self.__core_only():
            result = await self.db_season.log_jail_release(jail_id, released_on)
        return result

    async def get_active_jails(self) -> list[UserJail]:
        result = await self.db_core.get_active_jails()
        if not self.__core_only():
            result = await self.db_season.get_active_jails()
        return result

    async def get_jail(self, jail_id: int) -> UserJail:
        result = await self.db_core.get_jail(jail_id)
        if not self.__core_only():
            result = await self.db_season.get_jail(jail_id)
        return result

    async def get_jails_by_guild(self, guild_id: int) -> list[UserJail]:
        result = await self.db_core.get_jails_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_jails_by_guild(guild_id)
        return result

    async def get_active_jails_by_guild(self, guild_id: int) -> list[UserJail]:
        result = await self.db_core.get_active_jails_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_active_jails_by_guild(guild_id)
        return result

    async def get_active_jails_by_member(
        self, guild_id: int, user_id: int
    ) -> list[UserJail]:
        result = await self.db_core.get_active_jails_by_member(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_active_jails_by_member(guild_id, user_id)
        return result

    async def get_jail_events_by_jail(self, jail_id: int) -> list[JailEvent]:
        result = await self.db_core.get_jail_events_by_jail(jail_id)
        if not self.__core_only():
            result = await self.db_season.get_jail_events_by_jail(jail_id)
        return result

    async def get_jail_events_by_user(self, user_id: int) -> list[JailEvent]:
        result = await self.db_core.get_jail_events_by_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_jail_events_by_user(user_id)
        return result

    async def get_jail_events_affecting_user(self, user_id: int) -> list[JailEvent]:
        result = await self.db_core.get_jail_events_affecting_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_jail_events_affecting_user(user_id)
        return result

    async def get_jail_events_by_guild(
        self, guild_id: int
    ) -> dict[UserJail, list[JailEvent]]:
        result = await self.db_core.get_jail_events_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_jail_events_by_guild(guild_id)
        return result

    async def get_timeout_events_by_user(self, user_id: int) -> list[TimeoutEvent]:
        result = await self.db_core.get_timeout_events_by_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_timeout_events_by_user(user_id)
        return result

    async def get_timeout_events_by_guild(self, guild_id: int) -> list[TimeoutEvent]:
        result = await self.db_core.get_timeout_events_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_timeout_events_by_guild(guild_id)
        return result

    async def get_spam_events_by_user(self, user_id: int) -> list[SpamEvent]:
        result = await self.db_core.get_spam_events_by_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_spam_events_by_user(user_id)
        return result

    async def get_spam_events_by_guild(self, guild_id: int) -> list[SpamEvent]:
        result = await self.db_core.get_spam_events_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_spam_events_by_guild(guild_id)
        return result

    async def get_interaction_events_by_user(
        self, user_id: int
    ) -> list[InteractionEvent]:
        result = await self.db_core.get_interaction_events_by_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_interaction_events_by_user(user_id)
        return result

    async def get_interaction_events_affecting_user(
        self, user_id: int
    ) -> list[InteractionEvent]:
        result = await self.db_core.get_interaction_events_affecting_user(user_id)
        if not self.__core_only():
            result = await self.db_season.get_interaction_events_affecting_user(user_id)
        return result

    async def get_guild_interaction_events(
        self, guild_id: int, interaction_type: UserInteraction
    ) -> list[InteractionEvent]:
        result = await self.db_core.get_guild_interaction_events(
            guild_id, interaction_type
        )
        if not self.__core_only():
            result = await self.db_season.get_guild_interaction_events(
                guild_id, interaction_type
            )
        return result

    async def get_random_quote(self, guild_id: int) -> Quote:
        result = await self.db_core.get_random_quote(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_random_quote(guild_id)
        return result

    async def get_random_quote_by_user(self, guild_id: int, user_id: int) -> Quote:
        result = await self.db_core.get_random_quote_by_user(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_random_quote_by_user(guild_id, user_id)
        return result

    async def get_lootbox_items(self, lootbox_id: int) -> list[ItemType]:
        result = await self.db_core.get_lootbox_items(lootbox_id)
        if not self.__core_only():
            result = await self.db_season.get_lootbox_items(lootbox_id)
        return result

    async def get_loot_box_by_message_id(
        self, guild_id: int, message_id: int
    ) -> LootBox:
        result = await self.db_core.get_loot_box_by_message_id(guild_id, message_id)
        if not self.__core_only():
            result = await self.db_season.get_loot_box_by_message_id(
                guild_id, message_id
            )
        return result

    async def get_last_loot_box_event(self, guild_id: int):
        result = await self.db_core.get_last_loot_box_event(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_last_loot_box_event(guild_id)
        return result

    async def get_member_beans(self, guild_id: int, user_id: int) -> int:
        result = await self.db_core.get_member_beans(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_member_beans(guild_id, user_id)
        return result

    async def get_guild_beans(self, guild_id: int) -> dict[int, int]:
        result = await self.db_core.get_guild_beans(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_guild_beans(guild_id)
        return result

    async def get_guild_beans_rankings_current(self, guild_id: int) -> dict[int, int]:
        result = await self.db_core.get_guild_beans_rankings_current(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_guild_beans_rankings_current(guild_id)
        return result

    async def get_guild_beans_rankings(self, guild_id: int) -> dict[int, int]:
        result = await self.db_core.get_guild_beans_rankings(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_guild_beans_rankings(guild_id)
        return result

    async def get_lootbox_purchases_by_guild(
        self, guild_id: int, until: int = None
    ) -> dict[int, int]:
        result = await self.db_core.get_lootbox_purchases_by_guild(guild_id, until)
        if not self.__core_only():
            result = await self.db_season.get_lootbox_purchases_by_guild(
                guild_id, until
            )
        return result

    async def get_beans_daily_gamba_count(
        self,
        guild_id: int,
        user_id: int,
        beans_event_type: BeansEventType,
        min_value: int,
        date: int,
    ) -> int:
        result = await self.db_core.get_beans_daily_gamba_count(
            guild_id, user_id, beans_event_type, min_value, date
        )
        if not self.__core_only():
            result = await self.db_season.get_beans_daily_gamba_count(
                guild_id, user_id, beans_event_type, min_value, date
            )
        return result

    async def get_last_beans_event(
        self, guild_id: int, user_id: int, beans_event_type: BeansEventType
    ) -> BeansEvent:
        result = await self.db_core.get_last_beans_event(
            guild_id, user_id, beans_event_type
        )
        if not self.__core_only():
            result = await self.db_season.get_last_beans_event(
                guild_id, user_id, beans_event_type
            )
        return result

    async def get_lottery_data(self, guild_id: int) -> dict[int, int]:
        result = await self.db_core.get_lottery_data(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_lottery_data(guild_id)
        return result

    async def get_item_counts_by_guild(
        self, guild_id: int
    ) -> dict[int, dict[ItemType, int]]:
        result = await self.db_core.get_item_counts_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_item_counts_by_guild(guild_id)
        return result

    async def get_item_counts_by_user(
        self, guild_id: int, user_id: int
    ) -> dict[ItemType, int]:
        result = await self.db_core.get_item_counts_by_user(guild_id, user_id)
        if not self.__core_only():
            result = await self.db_season.get_item_counts_by_user(guild_id, user_id)
        return result

    async def get_prediction_by_id(self, prediction_id: int) -> Prediction:
        result = await self.db_core.get_prediction_by_id(prediction_id)
        if not self.__core_only():
            result = await self.db_season.get_prediction_by_id(prediction_id)
        return result

    async def get_predictions_by_guild(
        self, guild_id: int, states: list[PredictionState] = None
    ) -> list[Prediction]:
        result = await self.db_core.get_predictions_by_guild(guild_id, states)
        if not self.__core_only():
            result = await self.db_season.get_predictions_by_guild(guild_id, states)
        return result

    async def get_prediction_bets(
        self, predictions: list[Prediction]
    ) -> dict[int, int]:
        result = await self.db_core.get_prediction_bets(predictions)
        if not self.__core_only():
            result = await self.db_season.get_prediction_bets(predictions)
        return result

    async def get_prediction_bets_by_outcome(self, outcome_id: int) -> dict[int, int]:
        result = await self.db_core.get_prediction_bets_by_outcome(outcome_id)
        if not self.__core_only():
            result = await self.db_season.get_prediction_bets_by_outcome(outcome_id)
        return result

    async def get_prediction_bets_by_id(self, prediction_id: int) -> dict[int, int]:
        result = await self.db_core.get_prediction_bets_by_id(prediction_id)
        if not self.__core_only():
            result = await self.db_season.get_prediction_bets_by_id(prediction_id)
        return result

    async def get_prediction_bets_by_user(
        self, guild_id: int, member_id: int
    ) -> dict[int, tuple[int, int]]:
        result = await self.db_core.get_prediction_bets_by_user(guild_id, member_id)
        if not self.__core_only():
            result = await self.db_season.get_prediction_bets_by_user(
                guild_id, member_id
            )
        return result

    async def get_prediction_winning_outcome(self, prediction_id: int) -> int:
        result = await self.db_core.get_prediction_winning_outcome(prediction_id)
        if not self.__core_only():
            result = await self.db_season.get_prediction_winning_outcome(prediction_id)
        return result

    async def get_prediction_stats_by_prediction(
        self, prediction: Prediction
    ) -> PredictionStats:
        result = await self.db_core.get_prediction_stats_by_prediction(prediction)
        if not self.__core_only():
            result = await self.db_season.get_prediction_stats_by_prediction(prediction)
        return result

    async def get_prediction_stats_by_guild(
        self, guild_id: int, states: list[PredictionState] = None
    ) -> list[PredictionStats]:
        result = await self.db_core.get_prediction_stats_by_guild(guild_id, states)
        if not self.__core_only():
            result = await self.db_season.get_prediction_stats_by_guild(
                guild_id, states
            )
        return result

    async def get_last_bat_event_by_target(
        self, guild_id: int, target_user_id: int
    ) -> BatEvent:
        result = await self.db_core.get_last_bat_event_by_target(
            guild_id, target_user_id
        )
        if not self.__core_only():
            result = await self.db_season.get_last_bat_event_by_target(
                guild_id, target_user_id
            )
        return result

    async def get_lootboxes_by_guild(self, guild_id: int) -> list[tuple[int, LootBox]]:
        result = await self.db_core.get_lootboxes_by_guild(guild_id)
        if not self.__core_only():
            result = await self.db_season.get_lootboxes_by_guild(guild_id)
        return result

    async def get_guild_beans_events(
        self, guild_id: int, event_types: list[BeansEventType]
    ) -> list[BeansEvent]:
        result = await self.db_core.get_guild_beans_events(guild_id, event_types)
        if not self.__core_only():
            result = await self.db_season.get_guild_beans_events(guild_id, event_types)
        return result
