import datetime
import json
from typing import Any

import aiosqlite
import discord
from bot_util import BotUtil
from control.logger import BotLogger
from discord.ext import commands
from events.bat_event import BatEvent
from events.beans_event import BeansEvent, BeansEventType
from events.bot_event import BotEvent
from events.garden_event import GardenEvent
from events.interaction_event import InteractionEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.lootbox_event import LootBoxEvent
from events.prediction_event import PredictionEvent
from events.quote_event import QuoteEvent
from events.spam_event import SpamEvent
from events.timeout_event import TimeoutEvent
from events.types import (
    EventType,
    GardenEventType,
    LootBoxEventType,
    PredictionEventType,
)
from items import BaseSeed
from items.types import ItemState, ItemType
from view.types import EmojiType

from datalayer.garden import Plot, PlotModifiers, UserGarden
from datalayer.jail import UserJail
from datalayer.lootbox import LootBox
from datalayer.prediction import Prediction
from datalayer.prediction_stats import PredictionStats
from datalayer.quote import Quote
from datalayer.types import (
    PlantType,
    PredictionState,
    Season,
    SeasonDate,
    UserInteraction,
)


class Database:

    SETTINGS_TABLE = "guildsettings"
    SETTINGS_GUILD_ID_COL = "gset_guild_id"
    SETTINGS_MODULE_COL = "gset_module"
    SETTINGS_KEY_COL = "gset_key"
    SETTINGS_VALUE_COL = "gset_value"
    CREATE_SETTINGS_TABLE = f"""
    CREATE TABLE if not exists {SETTINGS_TABLE} (
        {SETTINGS_GUILD_ID_COL} INTEGER, 
        {SETTINGS_MODULE_COL} TEXT, 
        {SETTINGS_KEY_COL} TEXT, 
        {SETTINGS_VALUE_COL}, 
        PRIMARY KEY ({SETTINGS_GUILD_ID_COL}, {SETTINGS_MODULE_COL}, {SETTINGS_KEY_COL})
    );"""

    TIMEOUT_TRACKER_TABLE = "timeout_tracking"
    TIMEOUT_TRACKER_GUILD_ID_COL = "titr_guild_id"
    TIMEOUT_TRACKER_MEMBER_COL = "titr_member"
    TIMEOUT_TRACKER_COUNT_COL = "titr_count"
    CREATE_TIMEOUT_TRACKER_TABLE = f"""
    CREATE TABLE if not exists {TIMEOUT_TRACKER_TABLE} (
        {TIMEOUT_TRACKER_GUILD_ID_COL} INTEGER,
        {TIMEOUT_TRACKER_MEMBER_COL} INTEGER, 
        {TIMEOUT_TRACKER_COUNT_COL} INTEGER,
        PRIMARY KEY ({TIMEOUT_TRACKER_GUILD_ID_COL}, {TIMEOUT_TRACKER_MEMBER_COL})
    );"""

    JAIL_TABLE = "jail"
    JAIL_ID_COL = "jail_id"
    JAIL_GUILD_ID_COL = "jail_guild_id"
    JAIL_MEMBER_COL = "jail_member"
    JAIL_JAILED_ON_COL = "jail_jailed_on"
    JAIL_RELEASED_ON_COL = "jail_released_on"
    CREATE_JAIL_TABLE = f"""
    CREATE TABLE if not exists {JAIL_TABLE} (
        {JAIL_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {JAIL_GUILD_ID_COL} INTEGER, 
        {JAIL_MEMBER_COL} INTEGER, 
        {JAIL_JAILED_ON_COL} INTEGER, 
        {JAIL_RELEASED_ON_COL} INTEGER
    );"""

    EVENT_TABLE = "events"
    EVENT_ID_COL = "evnt_id"
    EVENT_TIMESTAMP_COL = "evnt_timestamp"
    EVENT_GUILD_ID_COL = "evnt_guild_id"
    EVENT_TYPE_COL = "evnt_type"
    CREATE_EVENT_TABLE = f"""
    CREATE TABLE if not exists {EVENT_TABLE} (
        {EVENT_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT, 
        {EVENT_TIMESTAMP_COL} INTEGER,
        {EVENT_GUILD_ID_COL} INTEGER,
        {EVENT_TYPE_COL} TEXT
    );"""

    INTERACTION_EVENT_TABLE = "interactionevents"
    INTERACTION_EVENT_ID_COL = "inev_id"
    INTERACTION_EVENT_TYPE_COL = "inev_type"
    INTERACTION_EVENT_FROM_COL = "inev_from_member"
    INTERACTION_EVENT_TO_COL = "inev_to_member"
    CREATE_INTERACTION_EVENT_TABLE = f"""
    CREATE TABLE if not exists {INTERACTION_EVENT_TABLE} (
        {INTERACTION_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {INTERACTION_EVENT_TYPE_COL} TEXT, 
        {INTERACTION_EVENT_FROM_COL} INTEGER, 
        {INTERACTION_EVENT_TO_COL} INTEGER,
        PRIMARY KEY ({INTERACTION_EVENT_ID_COL})
    );"""

    JAIL_EVENT_TABLE = "jailevents"
    JAIL_EVENT_ID_COL = "jaev_id"
    JAIL_EVENT_TYPE_COL = "jaev_type"
    JAIL_EVENT_BY_COL = "jaev_by"
    JAIL_EVENT_DURATION_COL = "jaev_duration"
    JAIL_EVENT_JAILREFERENCE_COL = "jaev_sentence_id"
    CREATE_JAIL_EVENT_TABLE = f"""
    CREATE TABLE if not exists {JAIL_EVENT_TABLE} (
        {JAIL_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {JAIL_EVENT_TYPE_COL} TEXT, 
        {JAIL_EVENT_BY_COL} INTEGER, 
        {JAIL_EVENT_DURATION_COL} INTEGER, 
        {JAIL_EVENT_JAILREFERENCE_COL} INTEGER REFERENCES {JAIL_TABLE} ({JAIL_ID_COL}),
        PRIMARY KEY ({JAIL_EVENT_ID_COL})
    );"""

    TIMEOUT_EVENT_TABLE = "timeoutevents"
    TIMEOUT_EVENT_ID_COL = "toev_id"
    TIMEOUT_EVENT_MEMBER_COL = "toev_member"
    TIMEOUT_EVENT_DURATION_COL = "toev_duration"
    CREATE_TIMEOUT_EVENT_TABLE = f"""
    CREATE TABLE if not exists {TIMEOUT_EVENT_TABLE} (
        {TIMEOUT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {TIMEOUT_EVENT_MEMBER_COL} INTEGER, 
        {TIMEOUT_EVENT_DURATION_COL} INTEGER,
        PRIMARY KEY ({TIMEOUT_EVENT_ID_COL})
    );"""

    SPAM_EVENT_TABLE = "spamevents"
    SPAM_EVENT_ID_COL = "spev_id"
    SPAM_EVENT_MEMBER_COL = "spev_member"
    CREATE_SPAM_EVENT_TABLE = f"""
    CREATE TABLE if not exists {SPAM_EVENT_TABLE} (
        {SPAM_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {SPAM_EVENT_MEMBER_COL} INTEGER, 
        PRIMARY KEY ({SPAM_EVENT_ID_COL})
    );"""

    QUOTE_TABLE = "quotes"
    QUOTE_ID_COL = "quot_id"
    QUOTE_GUILD_COL = "quot_guild_id"
    QUOTE_MEMBER_COL = "quot_member_id"
    QUOTE_MEMBER_NAME_COL = "quot_member_name"
    QUOTE_SAVED_BY_COL = "quot_saved_by"
    QUOTE_MESSAGE_COL = "quot_message_id"
    QUOTE_CHANNEL_COL = "quot_channel_id"
    QUOTE_TIMESTAMP_COL = "quot_timestamp"
    QUOTE_TEXT_COL = "quot_message_content"
    CREATE_QUOTE_TABLE = f"""
    CREATE TABLE if not exists {QUOTE_TABLE} (
        {QUOTE_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {QUOTE_GUILD_COL} INTEGER, 
        {QUOTE_MEMBER_COL} INTEGER, 
        {QUOTE_MEMBER_NAME_COL} TEXT, 
        {QUOTE_SAVED_BY_COL} INTEGER, 
        {QUOTE_MESSAGE_COL} INTEGER, 
        {QUOTE_CHANNEL_COL} INTEGER, 
        {QUOTE_TIMESTAMP_COL} INTEGER, 
        {QUOTE_TEXT_COL} TEXT
    );"""

    QUOTE_EVENT_TABLE = "quoteevents"
    QUOTE_EVENT_ID_COL = "quev_id"
    QUOTE_EVENT_REF_COL = "quev_quote_id"
    CREATE_QUOTE_EVENT_TABLE = f"""
    CREATE TABLE if not exists {QUOTE_EVENT_TABLE} (
        {QUOTE_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {QUOTE_EVENT_REF_COL} INTEGER REFERENCES {QUOTE_TABLE} ({QUOTE_ID_COL}),
        PRIMARY KEY ({QUOTE_EVENT_ID_COL})
    );"""

    BEANS_EVENT_TABLE = "beansevents"
    BEANS_EVENT_ID_COL = "bnev_id"
    BEANS_EVENT_MEMBER_COL = "bnev_member"
    BEANS_EVENT_TYPE_COL = "bnev_type"
    BEANS_EVENT_VALUE_COL = "bnev_value"
    CREATE_BEANS_EVENT_TABLE = f"""
    CREATE TABLE if not exists {BEANS_EVENT_TABLE} (
        {BEANS_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {BEANS_EVENT_MEMBER_COL} INTEGER, 
        {BEANS_EVENT_TYPE_COL} TEXT,
        {BEANS_EVENT_VALUE_COL} INTEGER,
        PRIMARY KEY ({BEANS_EVENT_ID_COL})
    );"""

    INVENTORY_ITEM_TABLE = "inventoryitems"
    INVENTORY_ITEM_GUILD_COL = "init_guild_id"
    INVENTORY_ITEM_MEMBER_COL = "init_member_id"
    INVENTORY_ITEM_ITEM_TYPE_COL = "init_item_type"
    INVENTORY_ITEM_STATE_COL = "init_item_state"
    CREATE_INVENTORY_ITEM_TABLE = f"""
    CREATE TABLE if not exists {INVENTORY_ITEM_TABLE} (
        {INVENTORY_ITEM_GUILD_COL} INTEGER, 
        {INVENTORY_ITEM_MEMBER_COL} INTEGER, 
        {INVENTORY_ITEM_ITEM_TYPE_COL} TEXT, 
        {INVENTORY_ITEM_STATE_COL} TEXT,
        PRIMARY KEY ({INVENTORY_ITEM_GUILD_COL}, {INVENTORY_ITEM_MEMBER_COL}, {INVENTORY_ITEM_ITEM_TYPE_COL})
    );"""

    INVENTORY_EVENT_TABLE = "inventoryevents"
    INVENTORY_EVENT_ID_COL = "inve_id"
    INVENTORY_EVENT_MEMBER_COL = "inve_member_id"
    INVENTORY_EVENT_ITEM_TYPE_COL = "inve_item_type"
    INVENTORY_EVENT_BEANS_EVENT_COL = "inve_beans_event_id"
    INVENTORY_EVENT_AMOUNT_COL = "inve_amount"
    CREATE_INVENTORY_EVENT_TABLE = f"""
    CREATE TABLE if not exists {INVENTORY_EVENT_TABLE} (
        {INVENTORY_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {INVENTORY_EVENT_MEMBER_COL} INTEGER, 
        {INVENTORY_EVENT_ITEM_TYPE_COL} TEXT, 
        {INVENTORY_EVENT_BEANS_EVENT_COL} INTEGER REFERENCES {BEANS_EVENT_TABLE} ({BEANS_EVENT_ID_COL}),
        {INVENTORY_EVENT_AMOUNT_COL} INTEGER,
        PRIMARY KEY ({INVENTORY_EVENT_ID_COL})
    );"""

    LOOTBOX_TABLE = "lootbox"
    LOOTBOX_ID_COL = "lobo_id"
    LOOTBOX_GUILD_COL = "lobo_guild_id"
    LOOTBOX_MESSAGE_ID_COL = "lobo_message_id_id"
    LOOTBOX_ITEM_TYPE_COL_OLD = "lobo_item_type"  # deprecated, legacy
    LOOTBOX_BEANS_COL = "lobo_beans"
    CREATE_LOOTBOX_TABLE = f"""
    CREATE TABLE if not exists {LOOTBOX_TABLE} (
        {LOOTBOX_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {LOOTBOX_GUILD_COL} INTEGER, 
        {LOOTBOX_MESSAGE_ID_COL} INTEGER, 
        {LOOTBOX_ITEM_TYPE_COL_OLD} TEXT, 
        {LOOTBOX_BEANS_COL} INTEGER
    );"""

    LOOTBOX_ITEM_TABLE = "lootboxitem"
    LOOTBOX_ITEM_ID_COL = "loit_id"
    LOOTBOX_ITEM_LOOTBOX_ID_COL = "loit_lootbox_id"
    LOOTBOX_ITEM_TYPE_COL = "loit_item_type"
    LOOTBOX_ITEM_AMOUNT_COL = "loit_item_amount"
    CREATE_LOOTBOX_ITEM_TABLE = f"""
    CREATE TABLE if not exists {LOOTBOX_ITEM_TABLE} (
        {LOOTBOX_ITEM_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {LOOTBOX_ITEM_LOOTBOX_ID_COL} INTEGER REFERENCES {LOOTBOX_TABLE} ({LOOTBOX_ID_COL}), 
        {LOOTBOX_ITEM_TYPE_COL} TEXT,
        {LOOTBOX_ITEM_AMOUNT_COL} INTEGER 
    );"""

    LOOTBOX_EVENT_TABLE = "lootboxevents"
    LOOTBOX_EVENT_ID_COL = "lbev_event_id"
    LOOTBOX_EVENT_LOOTBOX_ID_COL = "lbev_lootbox_id"
    LOOTBOX_EVENT_MEMBER_COL = "lbev_member_id"
    LOOTBOX_EVENT_TYPE_COL = "lbev_event_type"
    CREATE_LOOTBOX_EVENT_TABLE = f"""
    CREATE TABLE if not exists {LOOTBOX_EVENT_TABLE} (
        {LOOTBOX_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {LOOTBOX_EVENT_LOOTBOX_ID_COL} INTEGER REFERENCES {LOOTBOX_TABLE} ({LOOTBOX_ID_COL}),
        {LOOTBOX_EVENT_MEMBER_COL} INTEGER, 
        {LOOTBOX_EVENT_TYPE_COL} TEXT,
        PRIMARY KEY ({LOOTBOX_EVENT_ID_COL})
    );"""

    BAT_EVENT_TABLE = "batevents"
    BAT_EVENT_ID_COL = "btev_event_id"
    BAT_EVENT_USED_BY_COL = "btev_used_by_id"
    BAT_EVENT_TARGET_COL = "btev_target_id"
    BAT_EVENT_DURATION_COL = "btev_duration_id"
    CREATE_BAT_EVENT_TABLE = f"""
    CREATE TABLE if not exists {BAT_EVENT_TABLE} (
        {BAT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {BAT_EVENT_USED_BY_COL} INTEGER, 
        {BAT_EVENT_TARGET_COL} INTEGER, 
        {BAT_EVENT_DURATION_COL} INTEGER, 
        PRIMARY KEY ({BAT_EVENT_ID_COL})
    );"""

    CUSTOM_COLOR_TABLE = "customcolor"
    CUSTOM_COLOR_GUILD_COL = "cuco_guild_id"
    CUSTOM_COLOR_MEMBER_COL = "cuco_member_id"
    CUSTOM_COLOR_ROLE_COL = "cuco_role_id"
    CUSTOM_COLOR_COLOR_COL = "cuco_color"
    CREATE_CUSTOM_COLOR_TABLE = f"""
    CREATE TABLE if not exists {CUSTOM_COLOR_TABLE} (
        {CUSTOM_COLOR_GUILD_COL} INTEGER, 
        {CUSTOM_COLOR_MEMBER_COL}  INTEGER,
        {CUSTOM_COLOR_ROLE_COL} INTEGER, 
        {CUSTOM_COLOR_COLOR_COL} TEXT,
        PRIMARY KEY ({CUSTOM_COLOR_MEMBER_COL}, {CUSTOM_COLOR_GUILD_COL})
    );"""

    BULLY_REACT_TABLE = "bullyreact"
    BULLY_REACT_GUILD_COL = "buli_guild_id"
    BULLY_REACT_MEMBER_COL = "buli_member_id"
    BULLY_REACT_TARGET_COL = "buli_target_id"
    BULLY_REACT_EMOJI_TYPE_COL = "buli_type"
    BULLY_REACT_EMOJI_VALUE_COL = "buli_value"
    CREATE_BULLY_REACT_TABLE = f"""
    CREATE TABLE if not exists {BULLY_REACT_TABLE} (
        {BULLY_REACT_GUILD_COL} INTEGER, 
        {BULLY_REACT_MEMBER_COL}  INTEGER,
        {BULLY_REACT_TARGET_COL} INTEGER, 
        {BULLY_REACT_EMOJI_TYPE_COL} TEXT,
        {BULLY_REACT_EMOJI_VALUE_COL} TEXT,
        PRIMARY KEY ({BULLY_REACT_GUILD_COL}, {BULLY_REACT_MEMBER_COL})
    );"""

    PREDICTION_TABLE = "predictions"
    PREDICTION_ID_COL = "pred_id"
    PREDICTION_GUILD_ID_COL = "pred_guild_id"
    PREDICTION_AUTHOR_COL = "pred_author_id"
    PREDICTION_LOCK_TIMESTAMP_COL = "pred_lock_timestamp"
    PREDICTION_COMMENT_COL = "pred_comment"
    PREDICTION_CONTENT_COL = "pred_content"
    PREDICTION_STATE_COL = "pred_state"
    PREDICTION_MOD_ID_COL = "pred_moderator_id"
    CREATE_PREDICTION_TABLE = f"""
    CREATE TABLE if not exists {PREDICTION_TABLE} (
        {PREDICTION_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT,
        {PREDICTION_GUILD_ID_COL} INTEGER,
        {PREDICTION_AUTHOR_COL} INTEGER,
        {PREDICTION_CONTENT_COL} TEXT,
        {PREDICTION_STATE_COL} INTEGER,
        {PREDICTION_LOCK_TIMESTAMP_COL} INTEGER,
        {PREDICTION_COMMENT_COL} TEXT,
        {PREDICTION_MOD_ID_COL} INTEGER
    );"""

    PREDICTION_OUTCOME_TABLE = "predictionoutcomes"
    PREDICTION_OUTCOME_ID_COL = "proc_id"
    PREDICTION_OUTCOME_PREDICTION_ID_COL = "proc_prediction_id"
    PREDICTION_OUTCOME_CONTENT_COL = "proc_content"
    CREATE_PREDICTION_OUTCOME_TABLE = f"""
    CREATE TABLE if not exists {PREDICTION_OUTCOME_TABLE} (
        {PREDICTION_OUTCOME_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT,
        {PREDICTION_OUTCOME_PREDICTION_ID_COL} INTEGER REFERENCES {PREDICTION_TABLE} ({PREDICTION_ID_COL}),
        {PREDICTION_OUTCOME_CONTENT_COL} TEXT
    );"""

    PREDICTION_OVERVIEW_TABLE = "predictionoverviews"
    PREDICTION_OVERVIEW_MESSAGE_ID_COL = "prov_message_id"
    PREDICTION_OVERVIEW_CHANNEL_ID_COL = "prov_channel_id"
    PREDICTION_OVERVIEW_PREDICTION_ID_COL = "prov_prediction_id"
    CREATE_PREDICTION_OVERVIEW_TABLE = f"""
    CREATE TABLE if not exists {PREDICTION_OVERVIEW_TABLE} (
        {PREDICTION_OVERVIEW_MESSAGE_ID_COL} INTEGER,
        {PREDICTION_OVERVIEW_CHANNEL_ID_COL} INTEGER,
        {PREDICTION_OVERVIEW_PREDICTION_ID_COL} INTEGER REFERENCES {PREDICTION_TABLE} ({PREDICTION_ID_COL}),
        PRIMARY KEY ({PREDICTION_OVERVIEW_MESSAGE_ID_COL}, {PREDICTION_OVERVIEW_CHANNEL_ID_COL})
    );"""

    PREDICTION_EVENT_TABLE = "predictionevents"
    PREDICTION_EVENT_ID_COL = "prev_event_id"
    PREDICTION_EVENT_PREDICTION_ID_COL = "prev_prediction_id"
    PREDICTION_EVENT_OUTCOME_ID_COL = "prev_outcome_id"
    PREDICTION_EVENT_MEMBER_ID_COL = "prev_member_id"
    PREDICTION_EVENT_TYPE_COL = "prev_type"
    PREDICTION_EVENT_AMOUNT_COL = "prev_amount"
    CREATE_PREDICTION_EVENT_TABLE = f"""
    CREATE TABLE if not exists {PREDICTION_EVENT_TABLE} (
        {PREDICTION_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {PREDICTION_EVENT_PREDICTION_ID_COL} INTEGER REFERENCES {PREDICTION_TABLE} ({PREDICTION_ID_COL}), 
        {PREDICTION_EVENT_OUTCOME_ID_COL} INTEGER REFERENCES {PREDICTION_OUTCOME_TABLE} ({PREDICTION_OUTCOME_ID_COL}), 
        {PREDICTION_EVENT_MEMBER_ID_COL} INTEGER, 
        {PREDICTION_EVENT_TYPE_COL} TEXT, 
        {PREDICTION_EVENT_AMOUNT_COL} INTEGER, 
        PRIMARY KEY ({PREDICTION_EVENT_ID_COL})
    );"""

    GARDEN_TABLE = "gardens"
    GARDEN_ID = "grdn_id"
    GARDEN_GUILD_ID = "grdn_guild_id"
    GARDEN_USER_ID = "grdn_user_id"
    CREATE_GARDEN_TABLE = f"""
    CREATE TABLE if not exists {GARDEN_TABLE} (
        {GARDEN_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {GARDEN_GUILD_ID} INTEGER,
        {GARDEN_USER_ID} INTEGER,
        UNIQUE({GARDEN_GUILD_ID}, {GARDEN_USER_ID})
    );"""

    PLOT_TABLE = "plots"
    PLOT_ID = "plot_id"
    PLOT_GARDEN_ID = "plot_garden_id"
    PLOT_X = "plot_x"
    PLOT_Y = "plot_y"
    CREATE_PLOT_TABLE = f"""
    CREATE TABLE if not exists {PLOT_TABLE} (
        {PLOT_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {PLOT_GARDEN_ID} INTEGER REFERENCES {GARDEN_TABLE} ({GARDEN_ID}), 
        {PLOT_X} INTEGER,
        {PLOT_Y} INTEGER
    );"""

    GARDEN_EVENT_TABLE = "gardenevents"
    GARDEN_EVENT_ID_COL = "gaev_id"
    GARDEN_EVENT_GARDEN_ID_COL = "gaev_garden_id"
    GARDEN_EVENT_PLOT_ID_COL = "gaev_plot_id"
    GARDEN_EVENT_MEMBER_ID = "gaev_member_id"
    GARDEN_EVENT_TYPE_COL = "gaev_type"
    GARDEN_EVENT_PAYLOAD_COL = "gaev_payload"
    CREATE_GARDEN_EVENT_TABLE = f"""
    CREATE TABLE if not exists {GARDEN_EVENT_TABLE} (
        {GARDEN_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {GARDEN_EVENT_GARDEN_ID_COL} INTEGER REFERENCES {GARDEN_TABLE} ({GARDEN_ID}), 
        {GARDEN_EVENT_PLOT_ID_COL} INTEGER REFERENCES {PLOT_TABLE} ({PLOT_ID}), 
        {GARDEN_EVENT_MEMBER_ID} INTEGER, 
        {GARDEN_EVENT_TYPE_COL} TEXT, 
        {GARDEN_EVENT_PAYLOAD_COL} TEXT, 
        PRIMARY KEY ({GARDEN_EVENT_ID_COL})
    );"""

    PERMANENT_ITEMS = [
        ItemType.REACTION_SPAM,
        ItemType.LOTTERY_TICKET,
        ItemType.NAME_COLOR,
        ItemType.CATGIRL,
        ItemType.PRESTIGE_BEAN,
        ItemType.PERM_PET_BOOST,
        ItemType.INC_PET_BOOST,
        ItemType.PERM_SLAP_BOOST,
        ItemType.PERM_FART_BOOST,
        ItemType.PERM_PROTECTION,
    ]

    SEASONS = {
        Season.ALL_TIME: (SeasonDate.BEGINNING, None),
        Season.SEASON_1: (SeasonDate.BEGINNING, SeasonDate.SEASON_1),
        Season.CURRENT: (SeasonDate.SEASON_1, None),
    }

    def __init__(
        self,
        bot: commands.Bot,
        logger: BotLogger,
        db_file: str,
    ):
        self.bot = bot
        self.logger = logger
        self.db_file = db_file

    async def create_tables(self):
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute(self.CREATE_SETTINGS_TABLE)
            await db.execute(self.CREATE_JAIL_TABLE)
            await db.execute(self.CREATE_EVENT_TABLE)
            await db.execute(self.CREATE_QUOTE_TABLE)
            await db.execute(self.CREATE_TIMEOUT_TRACKER_TABLE)
            await db.execute(self.CREATE_INTERACTION_EVENT_TABLE)
            await db.execute(self.CREATE_JAIL_EVENT_TABLE)
            await db.execute(self.CREATE_TIMEOUT_EVENT_TABLE)
            await db.execute(self.CREATE_SPAM_EVENT_TABLE)
            await db.execute(self.CREATE_QUOTE_EVENT_TABLE)
            await db.execute(self.CREATE_BEANS_EVENT_TABLE)
            await db.execute(self.CREATE_INVENTORY_EVENT_TABLE)
            await db.execute(self.CREATE_LOOTBOX_TABLE)
            await db.execute(self.CREATE_LOOTBOX_EVENT_TABLE)
            await db.execute(self.CREATE_CUSTOM_COLOR_TABLE)
            await db.execute(self.CREATE_BULLY_REACT_TABLE)
            await db.execute(self.CREATE_BAT_EVENT_TABLE)
            await db.execute(self.CREATE_PREDICTION_TABLE)
            await db.execute(self.CREATE_PREDICTION_OUTCOME_TABLE)
            await db.execute(self.CREATE_PREDICTION_EVENT_TABLE)
            await db.execute(self.CREATE_PREDICTION_OVERVIEW_TABLE)
            await db.execute(self.CREATE_INVENTORY_ITEM_TABLE)
            await db.execute(self.CREATE_LOOTBOX_ITEM_TABLE)
            await db.execute(self.CREATE_PLOT_TABLE)
            await db.execute(self.CREATE_GARDEN_TABLE)
            await db.execute(self.CREATE_GARDEN_EVENT_TABLE)
            await db.commit()
            self.logger.log(
                "DB", f"Loaded DB version {aiosqlite.__version__} from {self.db_file}."
            )

    def __get_season_interval(self, season: Season):
        start_timestamp = self.SEASONS[season][0].value
        end_timestamp = self.SEASONS[season][1]
        if end_timestamp is None:
            end_timestamp = int(datetime.datetime.now().timestamp())
        else:
            end_timestamp = end_timestamp.value

        return start_timestamp, end_timestamp

    async def __query_select(self, query: str, task=None):
        async with aiosqlite.connect(self.db_file) as db:  # noqa: SIM117
            async with db.execute(query, task) as cursor:
                rows = await cursor.fetchall()
                headings = [x[0] for x in cursor.description]
                return self.__parse_rows(rows, headings)

    async def __query_insert(self, query: str, task=None) -> int:
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.execute(query, task)
            insert_id = cursor.lastrowid
            await db.commit()
            return insert_id

    def __parse_rows(self, rows, headings):
        if rows is None:
            return None

        output = []

        for row in rows:
            new_row = {}
            for idx, val in enumerate(row):
                new_row[headings[idx]] = val

            output.append(new_row)

        return output

    def __list_sanitizer(self, attribute_list: list[Any]) -> str:
        return "(" + ",".join(["?" for x in range(len(attribute_list))]) + ")"

    async def get_setting(self, guild_id: int, module: str, key: str):
        command = f"""
            SELECT * FROM {self.SETTINGS_TABLE} 
            WHERE {self.SETTINGS_GUILD_ID_COL}=? AND {self.SETTINGS_MODULE_COL}=? AND {self.SETTINGS_KEY_COL}=? 
            LIMIT 1;
        """
        task = (int(guild_id), str(module), str(key))

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None

        return json.loads(rows[0][self.SETTINGS_VALUE_COL])

    async def update_setting(self, guild_id: int, module: str, key: str, value):
        value = json.dumps(value)

        command = f"""
            INSERT INTO {self.SETTINGS_TABLE} ({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}, {self.SETTINGS_VALUE_COL}) 
            VALUES (?, ?, ?, ?) 
            ON CONFLICT({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}) 
            DO UPDATE SET {self.SETTINGS_VALUE_COL}=excluded.{self.SETTINGS_VALUE_COL};
        """
        task = (int(guild_id), str(module), str(key), value)

        return await self.__query_insert(command, task)

    async def __create_base_event(self, event: BotEvent) -> int:
        command = f"""
                INSERT INTO {self.EVENT_TABLE} (
                {self.EVENT_TIMESTAMP_COL}, 
                {self.EVENT_GUILD_ID_COL}, 
                {self.EVENT_TYPE_COL}) 
                VALUES (?, ?, ?);
            """
        task = (event.get_timestamp(), event.guild_id, event.type)

        return await self.__query_insert(command, task)

    async def __create_interaction_event(
        self, event_id: int, event: InteractionEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.INTERACTION_EVENT_TABLE} (
            {self.INTERACTION_EVENT_ID_COL},
            {self.INTERACTION_EVENT_TYPE_COL},
            {self.INTERACTION_EVENT_FROM_COL},
            {self.INTERACTION_EVENT_TO_COL}) 
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.interaction_type,
            event.from_user_id,
            event.to_user_id,
        )

        return await self.__query_insert(command, task)

    async def __create_timeout_event(self, event_id: int, event: TimeoutEvent) -> int:
        command = f"""
            INSERT INTO {self.TIMEOUT_EVENT_TABLE} (
            {self.TIMEOUT_EVENT_ID_COL},
            {self.TIMEOUT_EVENT_MEMBER_COL},
            {self.TIMEOUT_EVENT_DURATION_COL})
            VALUES (?, ?, ?);
        """
        task = (event_id, event.member_id, event.duration)

        return await self.__query_insert(command, task)

    async def __create_spam_event(self, event_id: int, event: SpamEvent) -> int:
        command = f"""
            INSERT INTO {self.SPAM_EVENT_TABLE} (
            {self.SPAM_EVENT_ID_COL},
            {self.SPAM_EVENT_MEMBER_COL})
            VALUES (?, ?);
        """
        task = (event_id, event.member_id)

        return await self.__query_insert(command, task)

    async def __create_jail_event(self, event_id: int, event: JailEvent) -> int:
        command = f"""
            INSERT INTO {self.JAIL_EVENT_TABLE} (
            {self.JAIL_EVENT_ID_COL},
            {self.JAIL_EVENT_TYPE_COL},
            {self.JAIL_EVENT_BY_COL},
            {self.JAIL_EVENT_DURATION_COL},
            {self.JAIL_EVENT_JAILREFERENCE_COL})
            VALUES (?, ?, ?, ?, ?);
        """
        task = (
            event_id,
            event.jail_event_type,
            event.caused_by_id,
            event.duration,
            event.jail_id,
        )

        return await self.__query_insert(command, task)

    async def __create_quote_event(self, event_id: int, event: QuoteEvent) -> int:
        command = f"""
            INSERT INTO {self.QUOTE_EVENT_TABLE} (
            {self.QUOTE_EVENT_ID_COL},
            {self.QUOTE_EVENT_REF_COL})
            VALUES (?, ?);
        """
        task = (event_id, event.quote_id)

        return await self.__query_insert(command, task)

    async def __create_beans_event(self, event_id: int, event: BeansEvent) -> int:
        command = f"""
            INSERT INTO {self.BEANS_EVENT_TABLE} (
            {self.BEANS_EVENT_ID_COL},
            {self.BEANS_EVENT_MEMBER_COL},
            {self.BEANS_EVENT_TYPE_COL},
            {self.BEANS_EVENT_VALUE_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.member_id,
            event.beans_event_type,
            event.value,
        )

        return await self.__query_insert(command, task)

    async def __create_inventory_event(
        self, event_id: int, event: InventoryEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.INVENTORY_EVENT_TABLE} (
            {self.INVENTORY_EVENT_ID_COL},
            {self.INVENTORY_EVENT_MEMBER_COL},
            {self.INVENTORY_EVENT_ITEM_TYPE_COL},
            {self.INVENTORY_EVENT_AMOUNT_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.member_id,
            event.item_type,
            event.amount,
        )

        return await self.__query_insert(command, task)

    async def __create_loot_box_event(self, event_id: int, event: LootBoxEvent) -> int:
        command = f"""
            INSERT INTO {self.LOOTBOX_EVENT_TABLE} (
            {self.LOOTBOX_EVENT_ID_COL},
            {self.LOOTBOX_EVENT_LOOTBOX_ID_COL},
            {self.LOOTBOX_EVENT_MEMBER_COL},
            {self.LOOTBOX_EVENT_TYPE_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.lootbox_id,
            event.member_id,
            event.loot_box_event_type,
        )

        return await self.__query_insert(command, task)

    async def __create_bat_event(self, event_id: int, event: BatEvent) -> int:
        command = f"""
            INSERT INTO {self.BAT_EVENT_TABLE} (
            {self.BAT_EVENT_ID_COL},
            {self.BAT_EVENT_USED_BY_COL},
            {self.BAT_EVENT_TARGET_COL},
            {self.BAT_EVENT_DURATION_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (event_id, event.used_by_id, event.target_id, event.duration)

        return await self.__query_insert(command, task)

    async def __create_prediction_event(
        self, event_id: int, event: PredictionEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.PREDICTION_EVENT_TABLE} (
            {self.PREDICTION_EVENT_ID_COL},
            {self.PREDICTION_EVENT_PREDICTION_ID_COL},
            {self.PREDICTION_EVENT_OUTCOME_ID_COL},
            {self.PREDICTION_EVENT_MEMBER_ID_COL},
            {self.PREDICTION_EVENT_TYPE_COL},
            {self.PREDICTION_EVENT_AMOUNT_COL})
            VALUES (?, ?, ?, ?, ?, ?);
        """
        task = (
            event_id,
            event.prediction_id,
            event.outcome_id,
            event.member_id,
            event.prediction_event_type,
            event.amount,
        )

        return await self.__query_insert(command, task)

    async def __create_garden_event(self, event_id: int, event: GardenEvent) -> int:
        command = f"""
            INSERT INTO {self.GARDEN_EVENT_TABLE} (
            {self.GARDEN_EVENT_ID_COL},
            {self.GARDEN_EVENT_GARDEN_ID_COL},
            {self.GARDEN_EVENT_PLOT_ID_COL},
            {self.GARDEN_EVENT_MEMBER_ID},
            {self.GARDEN_EVENT_TYPE_COL},
            {self.GARDEN_EVENT_PAYLOAD_COL})
            VALUES (?, ?, ?, ?, ?, ?);
        """
        task = (
            event_id,
            event.garden_id,
            event.plot_id,
            event.member_id,
            event.garden_event_type,
            event.payload,
        )

        return await self.__query_insert(command, task)

    async def log_event(self, event: BotEvent) -> int:
        event_id = await self.__create_base_event(event)

        if event_id is None:
            self.logger.error("DB", "Event creation error, id was NoneType")
            return None

        match event.type:
            case EventType.INTERACTION:
                return await self.__create_interaction_event(event_id, event)
            case EventType.JAIL:
                return await self.__create_jail_event(event_id, event)
            case EventType.TIMEOUT:
                return await self.__create_timeout_event(event_id, event)
            case EventType.QUOTE:
                return await self.__create_quote_event(event_id, event)
            case EventType.SPAM:
                return await self.__create_spam_event(event_id, event)
            case EventType.BEANS:
                return await self.__create_beans_event(event_id, event)
            case EventType.INVENTORY:
                return await self.__create_inventory_event(event_id, event)
            case EventType.LOOTBOX:
                return await self.__create_loot_box_event(event_id, event)
            case EventType.BAT:
                return await self.__create_bat_event(event_id, event)
            case EventType.PREDICTION:
                return await self.__create_prediction_event(event_id, event)
            case EventType.GARDEN:
                return await self.__create_garden_event(event_id, event)

    async def log_quote(self, quote: Quote) -> int:
        command = f"""
            INSERT INTO {self.QUOTE_TABLE} (
            {self.QUOTE_GUILD_COL},
            {self.QUOTE_MEMBER_COL},
            {self.QUOTE_MEMBER_NAME_COL},
            {self.QUOTE_SAVED_BY_COL},
            {self.QUOTE_MESSAGE_COL},
            {self.QUOTE_CHANNEL_COL},
            {self.QUOTE_TIMESTAMP_COL},
            {self.QUOTE_TEXT_COL}) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            quote.guild_id,
            quote.member_id,
            quote.member_name,
            quote.saved_by,
            quote.message_id,
            quote.channel_id,
            quote.get_timestamp(),
            quote.message_content,
        )

        return await self.__query_insert(command, task)

    async def log_lootbox(self, loot_box: LootBox) -> int:
        command = f"""
            INSERT INTO {self.LOOTBOX_TABLE} (
            {self.LOOTBOX_GUILD_COL},
            {self.LOOTBOX_MESSAGE_ID_COL},
            {self.LOOTBOX_BEANS_COL}) 
            VALUES (?, ?, ?);
        """
        task = (
            loot_box.guild_id,
            loot_box.message_id,
            loot_box.beans,
        )

        lootbox_id = await self.__query_insert(command, task)

        for item_type, amount in loot_box.items.items():

            command = f"""
                INSERT INTO {self.LOOTBOX_ITEM_TABLE} (
                {self.LOOTBOX_ITEM_LOOTBOX_ID_COL},
                {self.LOOTBOX_ITEM_TYPE_COL}, 
                {self.LOOTBOX_ITEM_AMOUNT_COL})
                VALUES (?, ?, ?);
            """

            task = (lootbox_id, item_type.value, amount)
            await self.__query_insert(command, task)

        return lootbox_id

    async def log_item_state(
        self,
        guild_id: int,
        user_id: int,
        item_type: ItemType,
        item_state: ItemState,
    ) -> int:
        command = f"""
            INSERT INTO {self.INVENTORY_ITEM_TABLE} (
                {self.INVENTORY_ITEM_GUILD_COL}, 
                {self.INVENTORY_ITEM_MEMBER_COL}, 
                {self.INVENTORY_ITEM_ITEM_TYPE_COL}, 
                {self.INVENTORY_ITEM_STATE_COL}) 
            VALUES (?, ?, ?, ?) 
            ON CONFLICT({self.INVENTORY_ITEM_GUILD_COL}, {self.INVENTORY_ITEM_MEMBER_COL}, {self.INVENTORY_ITEM_ITEM_TYPE_COL}) 
            DO UPDATE SET 
            {self.INVENTORY_ITEM_STATE_COL}=excluded.{self.INVENTORY_ITEM_STATE_COL};
        """
        task = (guild_id, user_id, item_type.value, item_state.value)

        return await self.__query_insert(command, task)

    async def get_user_item_states(
        self, guild_id: int, user_id: int
    ) -> dict[ItemType, ItemState]:
        command = f"""
            SELECT * FROM {self.INVENTORY_ITEM_TABLE}
            WHERE {self.INVENTORY_ITEM_GUILD_COL} = ? 
            AND {self.INVENTORY_ITEM_MEMBER_COL} = ?;
        """
        task = (guild_id, user_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return {
            ItemType(row[self.INVENTORY_ITEM_ITEM_TYPE_COL]): ItemState(
                row[self.INVENTORY_ITEM_STATE_COL]
            )
            for row in rows
        }

    async def log_bully_react(
        self,
        guild_id: int,
        user_id: int,
        target_id: int,
        emoji_type: EmojiType,
        emoji: discord.Emoji | str,
    ) -> int:
        command = f"""
            INSERT INTO {self.BULLY_REACT_TABLE} (
                {self.BULLY_REACT_GUILD_COL}, 
                {self.BULLY_REACT_MEMBER_COL}, 
                {self.BULLY_REACT_TARGET_COL}, 
                {self.BULLY_REACT_EMOJI_TYPE_COL}, 
                {self.BULLY_REACT_EMOJI_VALUE_COL}) 
            VALUES (?, ?, ?, ?, ?) 
            ON CONFLICT({self.BULLY_REACT_GUILD_COL}, {self.BULLY_REACT_MEMBER_COL}) 
            DO UPDATE SET 
            {self.BULLY_REACT_TARGET_COL}=excluded.{self.BULLY_REACT_TARGET_COL},
            {self.BULLY_REACT_EMOJI_TYPE_COL}=excluded.{self.BULLY_REACT_EMOJI_TYPE_COL},
            {self.BULLY_REACT_EMOJI_VALUE_COL}=excluded.{self.BULLY_REACT_EMOJI_VALUE_COL};
        """

        if emoji_type == EmojiType.CUSTOM:
            emoji = str(emoji.id)

        task = (guild_id, user_id, target_id, emoji_type.value, emoji)

        return await self.__query_insert(command, task)

    async def get_bully_react(
        self, guild_id: int, user_id: int
    ) -> tuple[int, discord.Emoji | str]:
        command = f"""
            SELECT * FROM {self.BULLY_REACT_TABLE}
            WHERE {self.BULLY_REACT_GUILD_COL} = ? 
            AND {self.BULLY_REACT_MEMBER_COL} = ? LIMIT 1;
        """
        task = (guild_id, user_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None, None

        emoji = rows[0][self.BULLY_REACT_EMOJI_VALUE_COL]
        if rows[0][self.BULLY_REACT_EMOJI_TYPE_COL] == EmojiType.CUSTOM.value:
            emoji = discord.utils.get(self.bot.emojis, id=int(emoji))

        return rows[0][self.BULLY_REACT_TARGET_COL], emoji

    async def log_custom_color(self, guild_id: int, user_id: int, color: str) -> int:
        command = f"""
            INSERT INTO {self.CUSTOM_COLOR_TABLE} ({self.CUSTOM_COLOR_GUILD_COL}, {self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_COLOR_COL}) 
            VALUES (?, ?, ?) 
            ON CONFLICT({self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_GUILD_COL}) 
            DO UPDATE SET {self.CUSTOM_COLOR_COLOR_COL}=excluded.{self.CUSTOM_COLOR_COLOR_COL};
        """
        task = (guild_id, user_id, color)

        return await self.__query_insert(command, task)

    async def get_custom_color(self, guild_id: int, user_id: int) -> str:
        command = f"""
            SELECT * FROM {self.CUSTOM_COLOR_TABLE}
            WHERE {self.CUSTOM_COLOR_MEMBER_COL} = ? 
            AND {self.CUSTOM_COLOR_GUILD_COL} = ? LIMIT 1;
        """
        task = (user_id, guild_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None

        return rows[0][self.CUSTOM_COLOR_COLOR_COL]

    async def log_custom_role(self, guild_id: int, user_id: int, role_id: int) -> int:
        command = f"""
            INSERT INTO {self.CUSTOM_COLOR_TABLE} ({self.CUSTOM_COLOR_GUILD_COL}, {self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_ROLE_COL}) 
            VALUES (?, ?, ?) 
            ON CONFLICT({self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_GUILD_COL}) 
            DO UPDATE SET {self.CUSTOM_COLOR_ROLE_COL}=excluded.{self.CUSTOM_COLOR_ROLE_COL}
            WHERE excluded.{self.CUSTOM_COLOR_ROLE_COL} IS NOT NULL ;
        """
        task = (guild_id, user_id, role_id)

        return await self.__query_insert(command, task)

    async def get_custom_role(self, guild_id: int, user_id: int) -> int:
        command = f"""
            SELECT * FROM {self.CUSTOM_COLOR_TABLE}
            WHERE {self.CUSTOM_COLOR_MEMBER_COL} = ? 
            AND {self.CUSTOM_COLOR_GUILD_COL} = ? LIMIT 1;
        """
        task = (user_id, guild_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None

        return rows[0][self.CUSTOM_COLOR_ROLE_COL]

    async def log_prediction(self, prediction: Prediction) -> int:
        command = f"""
            INSERT INTO {self.PREDICTION_TABLE} (
            {self.PREDICTION_GUILD_ID_COL},
            {self.PREDICTION_AUTHOR_COL},
            {self.PREDICTION_CONTENT_COL},
            {self.PREDICTION_STATE_COL},
            {self.PREDICTION_MOD_ID_COL},
            {self.PREDICTION_LOCK_TIMESTAMP_COL},
            {self.PREDICTION_COMMENT_COL}) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            prediction.guild_id,
            prediction.author_id,
            prediction.content,
            prediction.state,
            prediction.moderator_id,
            prediction.get_timestamp(),
            prediction.comment,
        )

        prediction_id = await self.__query_insert(command, task)

        for outcome in prediction.outcomes.values():
            command = f"""
                INSERT INTO {self.PREDICTION_OUTCOME_TABLE} (
                {self.PREDICTION_OUTCOME_PREDICTION_ID_COL},
                {self.PREDICTION_OUTCOME_CONTENT_COL}) 
                VALUES (?, ?);
            """
            task = (
                prediction_id,
                outcome,
            )
            await self.__query_insert(command, task)

        return prediction_id

    async def update_prediction(self, prediction: Prediction) -> int:
        command = f"""
            UPDATE {self.PREDICTION_TABLE} SET (
            {self.PREDICTION_CONTENT_COL},
            {self.PREDICTION_STATE_COL},
            {self.PREDICTION_MOD_ID_COL},
            {self.PREDICTION_LOCK_TIMESTAMP_COL},
            {self.PREDICTION_COMMENT_COL}) 
            = (?, ?, ?, ?, ?)
            WHERE {self.PREDICTION_ID_COL} = ?
        """
        task = (
            prediction.content,
            prediction.state,
            prediction.moderator_id,
            prediction.get_timestamp(),
            prediction.comment,
            prediction.id,
        )

        prediction_id = await self.__query_insert(command, task)

        for id, outcome in prediction.outcomes.items():
            command = f"""
                UPDATE {self.PREDICTION_OUTCOME_TABLE} SET 
                {self.PREDICTION_OUTCOME_CONTENT_COL} = ?
                WHERE {self.PREDICTION_OUTCOME_ID_COL} = ?
            """
            task = (
                outcome,
                id,
            )
            await self.__query_insert(command, task)

        return prediction_id

    async def clear_prediction_overview_messages(self, channel_id: int) -> int:
        command = f"""
            DELETE FROM {self.PREDICTION_OVERVIEW_TABLE}
            WHERE {self.PREDICTION_OVERVIEW_CHANNEL_ID_COL} = {int(channel_id)}
        """

        channel_id = await self.__query_insert(command)

        return channel_id

    async def add_prediction_overview_message(
        self, prediction_id: int, message_id: int, channel_id: int
    ) -> int:
        command = f"""
            INSERT INTO {self.PREDICTION_OVERVIEW_TABLE} 
            ({self.PREDICTION_OVERVIEW_MESSAGE_ID_COL}, 
            {self.PREDICTION_OVERVIEW_CHANNEL_ID_COL}, 
            {self.PREDICTION_OVERVIEW_PREDICTION_ID_COL})
            VALUES (?, ?, ?);
        """
        task = (message_id, channel_id, prediction_id)

        insert_id = await self.__query_insert(command, task)

        return insert_id

    async def get_prediction_overview_message(
        self, prediction_id: int, channel_id: int
    ) -> int:
        command = f"""
            SELECT * FROM {self.PREDICTION_OVERVIEW_TABLE}
            WHERE {self.PREDICTION_OVERVIEW_PREDICTION_ID_COL} = ?
            and {self.PREDICTION_OVERVIEW_CHANNEL_ID_COL} = ? LIMIT 1
        """
        task = (prediction_id, channel_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None

        return rows[0][self.PREDICTION_OVERVIEW_MESSAGE_ID_COL]

    async def fix_quote(self, quote: Quote, channel_id: int) -> int:
        command = f"""
            UPDATE {self.QUOTE_TABLE} 
            SET {self.QUOTE_CHANNEL_COL} = ?
            WHERE {self.QUOTE_ID_COL} = ?;
        """
        task = (channel_id, quote.id)

        return await self.__query_insert(command, task)

    async def increment_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        command = f"""
            INSERT INTO {self.TIMEOUT_TRACKER_TABLE} ({self.TIMEOUT_TRACKER_GUILD_ID_COL}, {self.TIMEOUT_TRACKER_MEMBER_COL}, {self.TIMEOUT_TRACKER_COUNT_COL}) 
            VALUES (?, ?, 1) 
            ON CONFLICT({self.TIMEOUT_TRACKER_GUILD_ID_COL}, {self.TIMEOUT_TRACKER_MEMBER_COL}) 
            DO UPDATE SET {self.TIMEOUT_TRACKER_COUNT_COL} = {self.TIMEOUT_TRACKER_COUNT_COL} + 1;
        """
        task = (guild_id, user_id)

        return await self.__query_insert(command, task)

    async def reset_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        command = f"""
            UPDATE {self.TIMEOUT_TRACKER_TABLE} 
            SET {self.TIMEOUT_TRACKER_COUNT_COL} = 0
            WHERE {self.TIMEOUT_TRACKER_GUILD_ID_COL} = ? 
            AND {self.TIMEOUT_TRACKER_MEMBER_COL} = ? ;
        """
        task = (guild_id, user_id)

        return await self.__query_insert(command, task)

    async def get_timeout_tracker_count(self, guild_id: int, user_id: int) -> int:
        command = f"""
            SELECT * FROM {self.TIMEOUT_TRACKER_TABLE}
            WHERE {self.TIMEOUT_TRACKER_GUILD_ID_COL} = ? 
            AND {self.TIMEOUT_TRACKER_MEMBER_COL} = ? LIMIT 1;
        """
        task = (guild_id, user_id)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0

        return rows[0][self.TIMEOUT_TRACKER_COUNT_COL]

    async def log_jail_sentence(self, jail: UserJail) -> UserJail:
        command = f"""
            INSERT INTO {self.JAIL_TABLE} (
            {self.JAIL_GUILD_ID_COL},
            {self.JAIL_MEMBER_COL},
            {self.JAIL_JAILED_ON_COL}) 
            VALUES (?, ?, ?);
        """
        task = (
            jail.guild_id,
            jail.member_id,
            jail.get_jailed_on_timestamp(),
        )

        insert_id = await self.__query_insert(command, task)
        return UserJail.from_jail(jail, jail_id=insert_id)

    async def log_jail_release(self, jail_id: int, released_on: int) -> int:
        command = f"""
            UPDATE {self.JAIL_TABLE} 
            SET {self.JAIL_RELEASED_ON_COL} = ?
            WHERE {self.JAIL_ID_COL} = ?;
        """
        task = (released_on, jail_id)

        return await self.__query_insert(command, task)

    async def get_active_jails(self) -> list[UserJail]:
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        """
        rows = await self.__query_select(command)
        if not rows:
            return []
        return [UserJail.from_db_row(row) for row in rows]

    async def get_jail(self, jail_id: int) -> UserJail:
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_ID_COL} = {int(jail_id)}
            LIMIT 1;
        """
        rows = await self.__query_select(command)

        if rows and len(rows) < 1:
            return None

        return UserJail.from_db_row(rows)

    async def get_jails_by_guild(self, guild_id: int) -> list[UserJail]:
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_GUILD_ID_COL} = {int(guild_id)};
        """
        rows = await self.__query_select(command)
        if not rows:
            return []
        return [UserJail.from_db_row(row) for row in rows]

    async def get_active_jails_by_guild(self, guild_id: int) -> list[UserJail]:
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_GUILD_ID_COL} = {int(guild_id)}
            AND {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        """
        rows = await self.__query_select(command)
        if not rows:
            return []
        return [UserJail.from_db_row(row) for row in rows]

    async def get_active_jails_by_member(
        self, guild_id: int, user_id: int
    ) -> list[UserJail]:
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_MEMBER_COL} = ?
            AND {self.JAIL_GUILD_ID_COL} = ?
            AND {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        """
        task = (user_id, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [UserJail.from_db_row(row) for row in rows]

    async def get_jail_events_by_jail(
        self, jail_id: int, season: Season = Season.CURRENT
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            WHERE {self.JAIL_EVENT_JAILREFERENCE_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (jail_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [JailEvent.from_db_row(row) for row in rows]

    async def get_jail_events_by_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            AND {self.JAIL_EVENT_BY_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [JailEvent.from_db_row(row) for row in rows]

    async def get_jail_events_affecting_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.JAIL_TABLE} 
            INNER JOIN {self.JAIL_EVENT_TABLE} ON {self.JAIL_TABLE}.{self.JAIL_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            WHERE {self.JAIL_TABLE}.{self.JAIL_MEMBER_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [JailEvent.from_db_row(row) for row in rows]

    async def get_jail_events_by_guild(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> dict[UserJail, list[JailEvent]]:
        jails = await self.get_jails_by_guild(guild_id)
        output = {}
        for jail in jails:
            output[jail] = await self.get_jail_events_by_jail(jail.id, season)

        return output

    async def get_timeout_events_by_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[TimeoutEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.TIMEOUT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.TIMEOUT_EVENT_TABLE}.{self.TIMEOUT_EVENT_ID_COL}
            WHERE {self.TIMEOUT_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [TimeoutEvent.from_db_row(row) for row in rows]

    async def get_timeout_events_by_guild(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> list[TimeoutEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.TIMEOUT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.TIMEOUT_EVENT_TABLE}.{self.TIMEOUT_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [TimeoutEvent.from_db_row(row) for row in rows]

    async def get_spam_events_by_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[SpamEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.SPAM_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.SPAM_EVENT_TABLE}.{self.SPAM_EVENT_ID_COL}
            WHERE {self.SPAM_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [SpamEvent.from_db_row(row) for row in rows]

    async def get_spam_events_by_guild(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> list[SpamEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.SPAM_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.SPAM_EVENT_TABLE}.{self.SPAM_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [SpamEvent.from_db_row(row) for row in rows]

    async def get_interaction_events_by_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.INTERACTION_EVENT_FROM_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]

    async def get_interaction_events_affecting_user(
        self, user_id: int, season: Season = Season.CURRENT
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.INTERACTION_EVENT_TO_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]

    async def get_guild_interaction_events(
        self,
        guild_id: int,
        interaction_type: UserInteraction,
        season: Season = Season.CURRENT,
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = ?
            AND {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_TYPE_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (guild_id, interaction_type.value, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]

    async def get_random_quote(self, guild_id: int) -> Quote:
        command = f""" 
            SELECT * FROM {self.QUOTE_TABLE} 
            WHERE {self.QUOTE_TABLE}.{self.QUOTE_GUILD_COL} = {int(guild_id)}
            ORDER BY RANDOM() LIMIT 1;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None
        return Quote.from_db_row(rows[0])

    async def get_random_quote_by_user(self, guild_id: int, user_id: int) -> Quote:
        command = f""" 
            SELECT * FROM {self.QUOTE_TABLE} 
            WHERE {self.QUOTE_TABLE}.{self.QUOTE_GUILD_COL} = ?
            AND {self.QUOTE_TABLE}.{self.QUOTE_MEMBER_COL} = ?
            ORDER BY RANDOM() LIMIT 1;
        """
        task = (guild_id, user_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None
        return Quote.from_db_row(rows[0])

    async def get_lootbox_items(self, lootbox_id: int) -> list[ItemType]:
        command = f""" 
            SELECT * FROM {self.LOOTBOX_ITEM_TABLE} 
            WHERE {self.LOOTBOX_ITEM_LOOTBOX_ID_COL} = {int(lootbox_id)};
        """
        rows = await self.__query_select(command)
        if not rows:
            return {}

        return {
            ItemType(row[self.LOOTBOX_ITEM_TYPE_COL]): int(
                row[self.LOOTBOX_ITEM_AMOUNT_COL]
            )
            for row in rows
        }

    async def get_loot_box_by_message_id(
        self, guild_id: int, message_id: int
    ) -> LootBox:
        command = f""" 
            SELECT * FROM {self.LOOTBOX_TABLE} 
            WHERE {self.LOOTBOX_MESSAGE_ID_COL} = ?
            AND {self.LOOTBOX_GUILD_COL} = ?
            LIMIT 1;
        """
        task = (message_id, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        items = await self.get_lootbox_items(rows[0][self.LOOTBOX_ID_COL])

        return LootBox.from_db_row(rows[0], items)

    async def get_last_loot_box_event(
        self, guild_id: int, season: Season = Season.CURRENT
    ):
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.LOOTBOX_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            WHERE {self.LOOTBOX_EVENT_TYPE_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC LIMIT 1;
        """
        task = (LootBoxEventType.DROP.value, guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return None
        return LootBoxEvent.from_db_row(rows[0])

    async def get_member_beans(
        self, guild_id: int, user_id: int, season: Season = Season.CURRENT
    ) -> int:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (user_id, guild_id, start_timestamp, end_timestamp)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0
        output = rows[0][f"SUM({self.BEANS_EVENT_VALUE_COL})"]
        return output if output is not None else 0

    async def get_guild_beans(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT {self.BEANS_EVENT_MEMBER_COL}, SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        """
        task = (guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        output = {
            row[self.BEANS_EVENT_MEMBER_COL]: row[f"SUM({self.BEANS_EVENT_VALUE_COL})"]
            for row in rows
        }

        return output

    async def get_guild_beans_rankings_current(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT {self.BEANS_EVENT_MEMBER_COL}, SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = ?
            WHERE {self.BEANS_EVENT_TYPE_COL} NOT IN (?, ?, ?, ?)
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        """
        task = (
            guild_id,
            BeansEventType.SHOP_PURCHASE.value,
            BeansEventType.USER_TRANSFER.value,
            BeansEventType.BALANCE_CHANGE.value,
            BeansEventType.SHOP_BUYBACK.value,
            start_timestamp,
            end_timestamp,
        )

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return {
            row[self.BEANS_EVENT_MEMBER_COL]: row[f"SUM({self.BEANS_EVENT_VALUE_COL})"]
            for row in rows
        }

    async def get_guild_beans_rankings(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT {self.BEANS_EVENT_MEMBER_COL}, MAX(rollingSum) as high_score 
            FROM (
                SELECT *, SUM({self.BEANS_EVENT_VALUE_COL}) 
                OVER ( 
                    PARTITION BY {self.BEANS_EVENT_MEMBER_COL} 
                    ORDER BY {self.BEANS_EVENT_ID_COL}
                ) as rollingSum 
                FROM {self.BEANS_EVENT_TABLE}
                INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
                AND {self.EVENT_GUILD_ID_COL} = ?
                WHERE {self.BEANS_EVENT_TYPE_COL} NOT IN (?, ?, ?, ?)
                AND {self.EVENT_TIMESTAMP_COL} > ?
                AND {self.EVENT_TIMESTAMP_COL} <= ?
            )
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        """
        task = (
            guild_id,
            BeansEventType.SHOP_PURCHASE.value,
            BeansEventType.USER_TRANSFER.value,
            BeansEventType.BALANCE_CHANGE.value,
            BeansEventType.SHOP_BUYBACK.value,
            start_timestamp,
            end_timestamp,
        )

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return {row[self.BEANS_EVENT_MEMBER_COL]: row["high_score"] for row in rows}

    async def get_member_beans_rankings(
        self, guild_id: int, member_id: int, season: Season = Season.CURRENT
    ) -> int:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT {self.BEANS_EVENT_MEMBER_COL}, MAX(rollingSum) as high_score 
            FROM (
                SELECT *, SUM({self.BEANS_EVENT_VALUE_COL}) 
                OVER ( 
                    PARTITION BY {self.BEANS_EVENT_MEMBER_COL} 
                    ORDER BY {self.BEANS_EVENT_ID_COL}
                ) as rollingSum 
                FROM {self.BEANS_EVENT_TABLE}
                INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
                AND {self.EVENT_GUILD_ID_COL} = ?
                WHERE {self.BEANS_EVENT_TYPE_COL} NOT IN (?, ?, ?, ?)
                AND {self.EVENT_TIMESTAMP_COL} > ?
                AND {self.EVENT_TIMESTAMP_COL} <= ?
                AND {self.BEANS_EVENT_MEMBER_COL} = ?
            )
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        """
        task = (
            guild_id,
            BeansEventType.SHOP_PURCHASE.value,
            BeansEventType.USER_TRANSFER.value,
            BeansEventType.BALANCE_CHANGE.value,
            BeansEventType.SHOP_BUYBACK.value,
            start_timestamp,
            end_timestamp,
            member_id,
        )

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0

        return rows[0]["high_score"]

    async def get_lootbox_purchases_by_guild(
        self, guild_id: int, until: int = None, season: Season = Season.CURRENT
    ) -> dict[int, int]:
        start_timestamp, _ = self.__get_season_interval(season)
        command = f"""
            SELECT {self.LOOTBOX_EVENT_MEMBER_COL}, COUNT({self.LOOTBOX_EVENT_TYPE_COL}) FROM {self.LOOTBOX_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = ?
            WHERE {self.LOOTBOX_EVENT_TYPE_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} < ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            GROUP BY {self.LOOTBOX_EVENT_MEMBER_COL};
        """
        if until is None:
            until = datetime.datetime.now().timestamp()

        task = (guild_id, LootBoxEventType.BUY.value, until, start_timestamp)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return {
            row[self.LOOTBOX_EVENT_MEMBER_COL]: row[
                f"COUNT({self.LOOTBOX_EVENT_TYPE_COL})"
            ]
            for row in rows
        }

    async def get_beans_daily_gamba_count(
        self,
        guild_id: int,
        user_id: int,
        beans_event_type: BeansEventType,
        min_value: int,
        date: int,
    ) -> int:
        command = f"""
            SELECT COUNT(*) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.BEANS_EVENT_TYPE_COL} = ?
            AND ABS({self.BEANS_EVENT_VALUE_COL}) >= ?
            AND {self.EVENT_TIMESTAMP_COL} >= ?;
        """
        task = (user_id, guild_id, beans_event_type, min_value, date)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0

        return rows[0]["COUNT(*)"]

    async def get_last_beans_event(
        self,
        guild_id: int,
        user_id: int,
        beans_event_type: BeansEventType,
        season: Season = Season.CURRENT,
    ) -> BeansEvent:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.BEANS_EVENT_TYPE_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC LIMIT 1;
        """
        task = (user_id, guild_id, beans_event_type, start_timestamp, end_timestamp)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        return BeansEvent.from_db_row(rows[0])

    async def get_lottery_data(self, guild_id: int) -> dict[int, int]:
        command = f"""
            SELECT {self.INVENTORY_EVENT_MEMBER_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.INVENTORY_EVENT_ITEM_TYPE_COL} = ?
            GROUP BY {self.INVENTORY_EVENT_MEMBER_COL};
        """
        task = (guild_id, ItemType.LOTTERY_TICKET)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}
        rows = {
            row[self.INVENTORY_EVENT_MEMBER_COL]: row[
                f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"
            ]
            for row in rows
            if row[f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"] > 0
        }
        return rows

    async def get_permanent_item_counts_by_guild(
        self, guild_id: int
    ) -> dict[int, dict[ItemType, int]]:
        item_types = [item.value for item in self.PERMANENT_ITEMS]
        list_sanitized = self.__list_sanitizer(item_types)
        command = f"""
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, {self.INVENTORY_EVENT_MEMBER_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.INVENTORY_EVENT_ITEM_TYPE_COL} in {list_sanitized}
            GROUP BY {self.INVENTORY_EVENT_MEMBER_COL}, {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        """
        task = (guild_id, *item_types)
        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        transformed = {}
        for row in rows:
            user_id = row[self.INVENTORY_EVENT_MEMBER_COL]
            item_type = ItemType(row[self.INVENTORY_EVENT_ITEM_TYPE_COL])
            amount = row[f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"]
            if amount <= 0:
                continue
            if user_id not in transformed:
                transformed[user_id] = {item_type: amount}
            else:
                transformed[user_id][item_type] = amount

        return transformed

    async def get_item_counts_by_guild(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> dict[int, dict[ItemType, int]]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, {self.INVENTORY_EVENT_MEMBER_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            GROUP BY {self.INVENTORY_EVENT_MEMBER_COL}, {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        """
        task = (guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)

        permanent_items = await self.get_permanent_item_counts_by_guild(guild_id)

        if not rows or len(rows) < 1:
            return permanent_items

        transformed = {}
        for row in rows:
            user_id = row[self.INVENTORY_EVENT_MEMBER_COL]
            item_type = ItemType(row[self.INVENTORY_EVENT_ITEM_TYPE_COL])
            amount = row[f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"]
            if amount <= 0:
                continue
            if user_id not in transformed:
                transformed[user_id] = {item_type: amount}
            else:
                transformed[user_id][item_type] = amount

        for user_id, item_counts in permanent_items.items():
            if user_id not in transformed:
                transformed[user_id] = permanent_items[user_id]
                continue
            for item_type, count in item_counts.items():
                transformed[user_id][item_type] = count

        return transformed

    async def get_permanent_item_counts_by_user(
        self, guild_id: int, user_id: int, item_types: list[ItemType] = None
    ) -> dict[ItemType, int]:
        permanent_items = self.PERMANENT_ITEMS
        if item_types is not None:
            permanent_items = [
                item_type
                for item_type in self.PERMANENT_ITEMS
                if item_type in item_types
            ]

        permanent_types = [item.value for item in permanent_items]
        list_sanitized = self.__list_sanitizer(permanent_types)
        command = f"""
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.INVENTORY_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.INVENTORY_EVENT_ITEM_TYPE_COL} IN {list_sanitized}
            GROUP BY {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        """
        task = (user_id, guild_id, *permanent_types)
        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return {
            ItemType(row[self.INVENTORY_EVENT_ITEM_TYPE_COL]): row[
                f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"
            ]
            for row in rows
            if row[f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"] > 0
        }

    async def get_item_counts_by_user(
        self,
        guild_id: int,
        user_id: int,
        season: Season = Season.CURRENT,
        item_types: list[ItemType] = None,
    ) -> dict[ItemType, int]:
        item_types_filter = ""

        start_timestamp, end_timestamp = self.__get_season_interval(season)
        task = (user_id, guild_id, start_timestamp, end_timestamp)

        if item_types is not None:
            types = [item.value for item in item_types]
            list_sanitized = self.__list_sanitizer(types)
            item_types_filter = (
                f"AND {self.INVENTORY_EVENT_ITEM_TYPE_COL} IN {list_sanitized}"
            )
            task = (user_id, guild_id, start_timestamp, end_timestamp, *types)

        command = f"""
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.INVENTORY_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            {item_types_filter}
            GROUP BY {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        """
        rows = await self.__query_select(command, task)

        permanent_items = await self.get_permanent_item_counts_by_user(
            guild_id, user_id, item_types
        )

        if not rows or len(rows) < 1:
            return permanent_items

        transformed = {
            ItemType(row[self.INVENTORY_EVENT_ITEM_TYPE_COL]): row[
                f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"
            ]
            for row in rows
            if row[f"SUM({self.INVENTORY_EVENT_AMOUNT_COL})"] > 0
        }
        result = transformed | permanent_items
        return result

    async def get_prediction_by_id(self, prediction_id: int) -> Prediction:

        command = f"""
            SELECT * FROM {self.PREDICTION_TABLE} 
            WHERE {self.PREDICTION_ID_COL} = {int(prediction_id)}
            LIMIT 1;
        """

        prediction_rows = await self.__query_select(command)
        if not prediction_rows or len(prediction_rows) < 1:
            return None

        prediction_row = prediction_rows[0]

        command = f"""
            SELECT * FROM {self.PREDICTION_OUTCOME_TABLE} 
            WHERE {self.PREDICTION_OUTCOME_PREDICTION_ID_COL} = {int(prediction_row[self.PREDICTION_ID_COL])};
        """

        outcome_rows = await self.__query_select(command)
        if not outcome_rows or len(outcome_rows) < 1:
            return None

        return Prediction.from_db_row(prediction_row, outcome_rows)

    async def get_predictions_by_guild(
        self, guild_id: int, states: list[PredictionState] = None
    ) -> list[Prediction]:

        if states is None:
            states = [x.value for x in PredictionState]
        else:
            states = [x.value for x in states]

        list_sanitized = self.__list_sanitizer(states)

        command = f"""
            SELECT * FROM {self.PREDICTION_TABLE} 
            WHERE {self.PREDICTION_GUILD_ID_COL} = ?
            AND {self.PREDICTION_STATE_COL} IN {list_sanitized};
        """

        task = (guild_id, *states)

        prediction_rows = await self.__query_select(command, task)
        if not prediction_rows or len(prediction_rows) < 1:
            return None

        predictions = []

        for row in prediction_rows:
            command = f"""
                SELECT * FROM {self.PREDICTION_OUTCOME_TABLE} 
                WHERE {self.PREDICTION_OUTCOME_PREDICTION_ID_COL} = {int(row[self.PREDICTION_ID_COL])};
            """

            outcome_rows = await self.__query_select(command)
            if not outcome_rows or len(outcome_rows) < 1:
                continue

            prediction = Prediction.from_db_row(row, outcome_rows)
            predictions.append(prediction)

        return predictions

    async def get_prediction_bets(
        self, predictions: list[Prediction]
    ) -> dict[int, int]:
        if predictions is None:
            return None

        prediction_ids = [prediction.id for prediction in predictions]
        list_sanitized = self.__list_sanitizer(prediction_ids)

        command = f"""
            SELECT *, SUM({self.PREDICTION_EVENT_AMOUNT_COL}) FROM {self.PREDICTION_EVENT_TABLE}
            WHERE {self.PREDICTION_EVENT_TYPE_COL} = ?
            AND {self.PREDICTION_EVENT_PREDICTION_ID_COL} IN {list_sanitized}
            GROUP BY {self.PREDICTION_EVENT_OUTCOME_ID_COL}
            ;
        """

        task = (PredictionEventType.PLACE_BET, *prediction_ids)

        bet_rows = await self.__query_select(command, task)
        if not bet_rows or len(bet_rows) < 1:
            return None

        return {
            row[self.PREDICTION_EVENT_OUTCOME_ID_COL]: row[
                f"SUM({self.PREDICTION_EVENT_AMOUNT_COL})"
            ]
            for row in bet_rows
        }

    async def get_prediction_bets_by_outcome(self, outcome_id: int) -> dict[int, int]:

        command = f"""
            SELECT * FROM {self.PREDICTION_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.PREDICTION_EVENT_TABLE}.{self.PREDICTION_EVENT_ID_COL}
            WHERE {self.PREDICTION_EVENT_TYPE_COL} = ?
            AND {self.PREDICTION_EVENT_OUTCOME_ID_COL} = ?;
        """

        task = (PredictionEventType.PLACE_BET, outcome_id)

        bet_rows = await self.__query_select(command, task)
        if not bet_rows or len(bet_rows) < 1:
            return {}

        output = {}

        for row in bet_rows:
            user_id = row[self.PREDICTION_EVENT_MEMBER_ID_COL]
            amount = row[self.PREDICTION_EVENT_AMOUNT_COL]

            if user_id not in output:
                output[user_id] = amount
                continue

            output[user_id] += amount

        return output

    async def get_prediction_bets_by_id(self, prediction_id: int) -> dict[int, int]:

        command = f"""
            SELECT * FROM {self.PREDICTION_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.PREDICTION_EVENT_TABLE}.{self.PREDICTION_EVENT_ID_COL}
            WHERE {self.PREDICTION_EVENT_TYPE_COL} = ?
            AND {self.PREDICTION_EVENT_PREDICTION_ID_COL} = ?;
        """

        task = (PredictionEventType.PLACE_BET, prediction_id)

        bet_rows = await self.__query_select(command, task)
        if not bet_rows or len(bet_rows) < 1:
            return {}

        output = {}

        for row in bet_rows:
            user_id = row[self.PREDICTION_EVENT_MEMBER_ID_COL]
            amount = row[self.PREDICTION_EVENT_AMOUNT_COL]

            if user_id not in output:
                output[user_id] = amount
                continue

            output[user_id] += amount

        return output

    async def get_prediction_bets_by_user(
        self, guild_id: int, member_id: int
    ) -> dict[int, tuple[int, int]]:

        command = f"""
            SELECT *, SUM({self.PREDICTION_EVENT_AMOUNT_COL}) FROM {self.PREDICTION_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.PREDICTION_EVENT_TABLE}.{self.PREDICTION_EVENT_ID_COL}
            WHERE {self.PREDICTION_EVENT_TYPE_COL} = ?
            AND {self.PREDICTION_EVENT_MEMBER_ID_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            GROUP BY {self.PREDICTION_EVENT_OUTCOME_ID_COL};
        """

        task = (PredictionEventType.PLACE_BET, member_id, guild_id)

        bet_rows = await self.__query_select(command, task)
        if not bet_rows or len(bet_rows) < 1:
            return {}

        return {
            row[self.PREDICTION_EVENT_PREDICTION_ID_COL]: (
                row[self.PREDICTION_EVENT_OUTCOME_ID_COL],
                row[f"SUM({self.PREDICTION_EVENT_AMOUNT_COL})"],
            )
            for row in bet_rows
        }

    async def get_prediction_winning_outcome(self, prediction_id: int) -> int:
        command = f"""
            SELECT * FROM {self.PREDICTION_EVENT_TABLE}
            WHERE {self.PREDICTION_EVENT_TYPE_COL} = ?
            AND {self.PREDICTION_EVENT_PREDICTION_ID_COL} = ?
            LIMIT 1;
        """

        task = (PredictionEventType.RESOLVE, prediction_id)

        bet_rows = await self.__query_select(command, task)
        if not bet_rows or len(bet_rows) < 1:
            return None

        return bet_rows[0][self.PREDICTION_EVENT_OUTCOME_ID_COL]

    async def get_prediction_stats_by_prediction(
        self, prediction: Prediction
    ) -> PredictionStats:
        prediction_bets = await self.get_prediction_bets([prediction])

        bets = None
        if prediction_bets is not None:
            bets = {
                outcome_id: bet
                for outcome_id, bet in prediction_bets.items()
                if outcome_id in prediction.outcomes
            }

        author_name = BotUtil.get_name(
            self.bot, prediction.guild_id, prediction.author_id, 40
        )
        mod_name = BotUtil.get_name(
            self.bot, prediction.guild_id, prediction.moderator_id, 30
        )
        winning_outcome_id = await self.get_prediction_winning_outcome(prediction.id)
        stats = PredictionStats(
            prediction, bets, author_name, mod_name, winning_outcome_id
        )
        return stats

    async def get_prediction_stats_by_guild(
        self, guild_id: int, states: list[PredictionState] = None
    ) -> list[PredictionStats]:
        predictions = await self.get_predictions_by_guild(guild_id, states)

        if predictions is None:
            return []

        prediction_bets = await self.get_prediction_bets(predictions)

        prediction_stats = []

        for prediction in predictions:
            bets = None
            if prediction_bets is not None:
                bets = {
                    outcome_id: bet
                    for outcome_id, bet in prediction_bets.items()
                    if outcome_id in prediction.outcomes
                }

            author_name = BotUtil.get_name(self.bot, guild_id, prediction.author_id, 40)
            mod_name = BotUtil.get_name(self.bot, guild_id, prediction.moderator_id, 30)
            winning_outcome_id = await self.get_prediction_winning_outcome(
                prediction.id
            )
            stats = PredictionStats(
                prediction, bets, author_name, mod_name, winning_outcome_id
            )
            prediction_stats.append(stats)
        return prediction_stats

    async def get_last_bat_event_by_target(
        self,
        guild_id: int,
        target_user_id: int,
        season: Season = Season.CURRENT,
    ) -> BatEvent:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.BAT_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BAT_EVENT_TABLE}.{self.BAT_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.BAT_EVENT_TARGET_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC LIMIT 1;
        """
        task = (guild_id, target_user_id, start_timestamp, end_timestamp)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        return BatEvent.from_db_row(rows[0])

    async def get_lootboxes_by_guild(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> list[tuple[int, LootBox]]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)

        lootbox_types = [LootBoxEventType.CLAIM.value, LootBoxEventType.OPEN.value]
        list_sanitized = self.__list_sanitizer(lootbox_types)

        command = f"""
            SELECT * FROM {self.LOOTBOX_TABLE}
            INNER JOIN {self.LOOTBOX_EVENT_TABLE} ON {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_LOOTBOX_ID_COL} = {self.LOOTBOX_TABLE}.{self.LOOTBOX_ID_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            LEFT JOIN {self.LOOTBOX_ITEM_TABLE} ON {self.LOOTBOX_ITEM_TABLE}.{self.LOOTBOX_ITEM_LOOTBOX_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_LOOTBOX_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            AND {self.LOOTBOX_EVENT_TYPE_COL} IN {list_sanitized};
        """
        task = (guild_id, start_timestamp, end_timestamp, *lootbox_types)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return [
            (
                row[self.LOOTBOX_EVENT_MEMBER_COL],
                LootBox.from_db_row(
                    row,
                    {
                        ItemType(item_row[self.LOOTBOX_ITEM_TYPE_COL]): int(
                            item_row[self.LOOTBOX_ITEM_AMOUNT_COL]
                        )
                        for item_row in rows
                        if item_row[self.LOOTBOX_ITEM_LOOTBOX_ID_COL]
                        == row[self.LOOTBOX_ID_COL]
                    },
                ),
            )
            for row in rows
        ]

    async def get_guild_beans_events(
        self,
        guild_id: int,
        event_types: list[BeansEventType],
        season: Season = Season.CURRENT,
    ) -> list[BeansEvent]:
        start_timestamp, end_timestamp = self.__get_season_interval(season)
        event_type_values = [event_type.value for event_type in event_types]
        list_sanitized = self.__list_sanitizer(event_type_values)

        command = f"""
            SELECT * FROM {self.BEANS_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            AND {self.BEANS_EVENT_TYPE_COL} IN {list_sanitized};
        """
        task = (guild_id, start_timestamp, end_timestamp, *event_type_values)

        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}

        return [BeansEvent.from_db_row(row) for row in rows]

    async def create_user_garden(self, guild_id: int, user_id: int):
        command = f"""
            INSERT OR IGNORE INTO {self.GARDEN_TABLE}
            ({self.GARDEN_GUILD_ID}, {self.GARDEN_USER_ID}) 
            VALUES(?, ?);
        """
        task = (guild_id, user_id)

        insert_id = await self.__query_insert(command, task)

        if insert_id != 0:
            command = f"""
                INSERT OR IGNORE INTO {self.PLOT_TABLE}
                ({self.PLOT_GARDEN_ID}, {self.PLOT_X}, {self.PLOT_Y}) 
                VALUES(?, ?, ?);
            """
            task = (insert_id, 0, 0)
            insert_id = await self.__query_insert(command, task)

    async def add_garden_plot(self, garden: UserGarden) -> UserGarden:

        plot_count = len(garden.plots)
        if plot_count >= UserGarden.MAX_PLOTS:
            return garden

        new_position = UserGarden.PLOT_ORDER[plot_count]

        command = f"""
                INSERT INTO {self.PLOT_TABLE}
                ({self.PLOT_GARDEN_ID}, {self.PLOT_X}, {self.PLOT_Y}) 
                VALUES(?, ?, ?);
            """
        task = (garden.id, new_position[0], new_position[1])
        insert_id = await self.__query_insert(command, task)

        plot = Plot(insert_id, garden.id, new_position[0], new_position[1])
        garden.plots.append(plot)
        return garden

    async def get_garden_plots(
        self, garden_id, season: Season = Season.CURRENT
    ) -> list[Plot]:
        command = f"""
            SELECT * FROM {self.GARDEN_TABLE}
            INNER JOIN {self.PLOT_TABLE} ON {self.PLOT_TABLE}.{self.PLOT_GARDEN_ID} = {self.GARDEN_TABLE}.{self.GARDEN_ID}
            WHERE {self.GARDEN_ID} = {int(garden_id)};
        """
        rows = await self.__query_select(command)
        if not rows or len(rows) < 1:
            return []

        plots: list[Plot] = []

        for row in rows:
            plot = Plot(
                row[self.PLOT_ID],
                garden_id,
                row[self.PLOT_X],
                row[self.PLOT_Y],
            )
            plots.append(plot)

        start_timestamp, end_timestamp = self.__get_season_interval(season)
        command = f"""
            SELECT * FROM {self.GARDEN_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.GARDEN_EVENT_TABLE}.{self.GARDEN_EVENT_ID_COL}
            WHERE {self.GARDEN_EVENT_GARDEN_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            AND {self.EVENT_TIMESTAMP_COL} <= ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC;
        """
        task = (garden_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return plots

        plot_plants = {}
        plot_water_events = {}
        plot_last_fertilized = {}
        flash_bean_events = []
        plot_notified = {}
        skip_list = []

        for row in rows:
            plot_id = row[self.GARDEN_EVENT_PLOT_ID_COL]
            type = GardenEventType(row[self.GARDEN_EVENT_TYPE_COL])
            payload = row[self.GARDEN_EVENT_PAYLOAD_COL]

            if (
                type == GardenEventType.HARVEST
                and payload == PlantType.YELLOW_BEAN.value
                and plot_id not in plot_last_fertilized
            ):
                plot_last_fertilized[plot_id] = GardenEvent.from_db_row(row)
            if (
                type in [GardenEventType.PLANT, GardenEventType.REMOVE]
                and payload == PlantType.FLASH_BEAN.value
            ):
                flash_bean_events.append(GardenEvent.from_db_row(row))

            if plot_id in skip_list:
                continue
            match type:
                case GardenEventType.PLANT:
                    plot_plants[plot_id] = GardenEvent.from_db_row(row)
                    skip_list.append(plot_id)
                case GardenEventType.WATER:
                    if plot_id not in plot_water_events:
                        plot_water_events[plot_id] = [GardenEvent.from_db_row(row)]
                    else:
                        plot_water_events[plot_id].append(GardenEvent.from_db_row(row))
                case GardenEventType.REMOVE | GardenEventType.HARVEST:
                    skip_list.append(plot_id)
                case GardenEventType.NOTIFICATION:
                    plot_notified[plot_id] = True

        result = []

        for plot in plots:
            if plot.id in plot_plants:
                event: GardenEvent = plot_plants[plot.id]
                plot.plant_datetime = event.datetime
                plot.plant = UserGarden.get_plant_by_type(event.payload)
            if plot.id in plot_notified:
                plot.notified = plot_notified[plot.id]

            modifiers = PlotModifiers()
            now = datetime.datetime.now()

            if plot.id in plot_water_events:
                modifiers.water_events = plot_water_events[plot.id]
            if plot.id in plot_last_fertilized:
                delta = now - plot_last_fertilized[plot.id].datetime
                modifiers.last_fertilized = delta.total_seconds() / Plot.TIME_MODIFIER
            modifiers.flash_bean_events = flash_bean_events

            plot.modifiers = modifiers
            result.append(plot)

        return result

    async def get_user_seeds(
        self, guild_id: int, user_id: int, season: Season = Season.CURRENT
    ) -> dict[PlantType, int]:
        user_balance = await self.get_member_beans(guild_id, user_id, season)
        user_seeds = {PlantType.BEAN: user_balance}

        seed_items = await self.get_item_counts_by_user(
            guild_id, user_id, season=season, item_types=BaseSeed.SEED_TYPES
        )

        for item_type, count in seed_items.items():
            user_seeds[BaseSeed.SEED_PLANT_MAP[item_type]] = count

        return user_seeds

    async def get_user_garden(
        self, guild_id: int, user_id: int, season: Season = Season.CURRENT
    ) -> UserGarden:
        await self.create_user_garden(guild_id, user_id)

        command = f"""
            SELECT * FROM {self.GARDEN_TABLE}
            WHERE {self.GARDEN_GUILD_ID} = ?
            AND {self.GARDEN_USER_ID} = ?
            LIMIT 1;
        """
        task = (guild_id, user_id)
        rows = await self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        garden_id = rows[0][self.GARDEN_ID]

        plots = await self.get_garden_plots(garden_id, season)
        user_seeds = await self.get_user_seeds(guild_id, user_id, season=season)

        return UserGarden(
            garden_id,
            guild_id,
            user_id,
            plots,
            user_seeds,
        )

    async def get_guild_gardens(
        self, guild_id: int, season: Season = Season.CURRENT
    ) -> list[UserGarden]:

        command = f"""
            SELECT * FROM {self.GARDEN_TABLE}
            WHERE {self.GARDEN_GUILD_ID} = {int(guild_id)};
        """
        rows = await self.__query_select(command)
        if not rows or len(rows) < 1:
            return []

        gardens = []

        for row in rows:
            garden_id = row[self.GARDEN_ID]
            user_id = row[self.GARDEN_USER_ID]

            plots = await self.get_garden_plots(garden_id, season)

            gardens.append(
                UserGarden(
                    garden_id,
                    guild_id,
                    user_id,
                    plots,
                    {},
                )
            )

        return gardens
