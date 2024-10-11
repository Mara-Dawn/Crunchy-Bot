import contextlib
import datetime
import json
from typing import Any

import aiosqlite
import discord
from discord.ext import commands

from bot_util import BotUtil
from combat.enchantments.enchantment import EffectEnchantment, Enchantment
from combat.enchantments.enchantments import *  # noqa: F403
from combat.enchantments.types import EnchantmentEffect, EnchantmentType
from combat.encounter import Encounter
from combat.enemies.types import EnemyType
from combat.equipment import CharacterEquipment
from combat.gear.bases import *  # noqa: F403
from combat.gear.default_gear import (
    DefaultAccessory1,
    DefaultAccessory2,
    DefaultCap,
    DefaultPants,
    DefaultShirt,
    DefaultStick,
    DefaultWand,
    Gear,
)
from combat.gear.gear import Droppable
from combat.gear.types import (
    Base,
    EquipmentSlot,
    GearBaseType,
    GearModifierType,
    Rarity,
)
from combat.gear.uniques import *  # noqa: F403
from combat.skills.skill import BaseSkill, Skill
from combat.skills.skills import *  # noqa: F403
from combat.skills.types import SkillType
from config import Config
from control.logger import BotLogger
from datalayer.garden import Plot, PlotModifiers, UserGarden
from datalayer.jail import UserJail
from datalayer.lootbox import LootBox
from datalayer.prediction import Prediction
from datalayer.prediction_stats import PredictionStats
from datalayer.quote import Quote
from datalayer.types import (
    PlantType,
    PredictionState,
    UserInteraction,
)
from events.bat_event import BatEvent
from events.beans_event import BeansEvent, BeansEventType
from events.bot_event import BotEvent
from events.combat_event import CombatEvent
from events.encounter_event import EncounterEvent
from events.equipment_event import EquipmentEvent
from events.garden_event import GardenEvent
from events.interaction_event import InteractionEvent
from events.inventory_batchevent import InventoryBatchEvent
from events.inventory_event import InventoryEvent
from events.jail_event import JailEvent
from events.karma_event import KarmaEvent
from events.lootbox_event import LootBoxEvent
from events.prediction_event import PredictionEvent
from events.quote_event import QuoteEvent
from events.spam_event import SpamEvent
from events.status_effect_event import StatusEffectEvent
from events.timeout_event import TimeoutEvent
from events.types import (
    CombatEventType,
    EncounterEventType,
    EquipmentEventType,
    EventType,
    GardenEventType,
    LootBoxEventType,
    PredictionEventType,
)
from items import BaseSeed
from items.types import ItemState, ItemType
from view.types import EmojiType


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

    GUILD_CURRENT_SEASON_TABLE = "guildseason"
    GUILD_CURRENT_SEASON_GUILD_ID_COL = "gdsn_guild_id"
    GUILD_CURRENT_SEASON_GUILD_LEVEL_COL = "gdsn_guild_level"
    CREATE_CURRENT_GUILD_SEASON_TABLE = f"""
    CREATE TABLE if not exists {GUILD_CURRENT_SEASON_TABLE} (
        {GUILD_CURRENT_SEASON_GUILD_ID_COL} INTEGER PRIMARY KEY,
        {GUILD_CURRENT_SEASON_GUILD_LEVEL_COL} INTEGER
    );"""

    GUILD_SEASON_TABLE = "guildseasonlog"
    GUILD_SEASON_GUILD_ID_COL = "gsnl_guild_id"
    GUILD_SEASON_SEASON_NR_COL = "gsnl_season_nr"
    GUILD_SEASON_END_TIMESTAMP_COL = "gsnl_end_timestamp"
    CREATE_GUILD_SEASON_TABLE = f"""
    CREATE TABLE if not exists {GUILD_SEASON_TABLE} (
        {GUILD_SEASON_GUILD_ID_COL} INTEGER,
        {GUILD_SEASON_SEASON_NR_COL} INTEGER,
        {GUILD_SEASON_END_TIMESTAMP_COL} INTEGER,
        PRIMARY KEY ({GUILD_SEASON_GUILD_ID_COL}, {GUILD_SEASON_SEASON_NR_COL})
    );"""

    ENCOUNTER_TABLE = "encounters"
    ENCOUNTER_ID_COL = "encn_id"
    ENCOUNTER_GUILD_ID_COL = "encn_guild_id"
    ENCOUNTER_ENEMY_TYPE_COL = "encn_enemy_type"
    ENCOUNTER_ENEMY_LEVEL_COL = "encn_enemy_level"
    ENCOUNTER_ENEMY_HEALTH_COL = "encn_enemy_health"
    ENCOUNTER_MESSAGE_ID_COL = "encn_message_id"
    ENCOUNTER_CHANNEL_ID_COL = "encn_channel_id"
    ENCOUNTER_OWNER_ID_COL = "encn_owner_id"
    CREATE_ENCOUNTER_TABLE = f"""
    CREATE TABLE if not exists {ENCOUNTER_TABLE} (
        {ENCOUNTER_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT,
        {ENCOUNTER_GUILD_ID_COL} INTEGER,
        {ENCOUNTER_ENEMY_TYPE_COL} TEXT,
        {ENCOUNTER_ENEMY_LEVEL_COL} INTEGER,
        {ENCOUNTER_ENEMY_HEALTH_COL} INTEGER,
        {ENCOUNTER_MESSAGE_ID_COL} INTEGER,
        {ENCOUNTER_CHANNEL_ID_COL} INTEGER,
        {ENCOUNTER_OWNER_ID_COL} INTEGER
    );"""

    ENCOUNTER_THREAD_TABLE = "encounterthreads"
    ENCOUNTER_THREAD_ID_COL = "enth_id"
    ENCOUNTER_THREAD_ENCOUNTER_ID_COL = "enth_encounter_id"
    ENCOUNTER_THREAD_GUILD_ID_COL = "enth_guild_id"
    ENCOUNTER_THREAD_CHANNEL_ID_COL = "enth_channel_id"
    CREATE_ENCOUNTER_THREAD_TABLE = f"""
    CREATE TABLE if not exists {ENCOUNTER_THREAD_TABLE} (
        {ENCOUNTER_THREAD_ID_COL} INTEGER,
        {ENCOUNTER_THREAD_ENCOUNTER_ID_COL} INTEGER REFERENCES {ENCOUNTER_TABLE} ({ENCOUNTER_ID_COL}), 
        {ENCOUNTER_THREAD_GUILD_ID_COL} INTEGER,
        {ENCOUNTER_THREAD_CHANNEL_ID_COL} INTEGER,
        PRIMARY KEY ({ENCOUNTER_THREAD_ENCOUNTER_ID_COL})
    );"""

    ENCOUNTER_EVENT_TABLE = "encounterevents"
    ENCOUNTER_EVENT_ID_COL = "enev_id"
    ENCOUNTER_EVENT_ENCOUNTER_ID_COL = "enev_encounter_id"
    ENCOUNTER_EVENT_MEMBER_ID = "enev_member_id"
    ENCOUNTER_EVENT_TYPE_COL = "enev_type"
    CREATE_ENCOUNTER_EVENT_TABLE = f"""
    CREATE TABLE if not exists {ENCOUNTER_EVENT_TABLE} (
        {ENCOUNTER_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {ENCOUNTER_EVENT_ENCOUNTER_ID_COL} INTEGER REFERENCES {ENCOUNTER_TABLE} ({ENCOUNTER_ID_COL}), 
        {ENCOUNTER_EVENT_MEMBER_ID} INTEGER, 
        {ENCOUNTER_EVENT_TYPE_COL} TEXT, 
        PRIMARY KEY ({ENCOUNTER_EVENT_ID_COL})
    );"""

    USER_GEAR_TABLE = "usergear"
    USER_GEAR_ID_COL = "usgr_id"
    USER_GEAR_GUILD_ID_COL = "usgr_guild_id"
    USER_GEAR_MEMBER_ID_COL = "usgr_member_id"
    USER_GEAR_NAME_COL = "usgr_name"
    USER_GEAR_BASE_TYPE_COL = "usgr_base_type"
    USER_GEAR_TYPE_COL = "usgr_type"
    USER_GEAR_LEVEL_COL = "usgr_level"
    USER_GEAR_RARITY_COL = "usgr_rarity"
    USER_GEAR_GENERATOR_VERSION_COL = "usgr_generator_version"
    USER_GEAR_IS_SCRAPPED_COL = "usgr_is_scrapped"
    USER_GEAR_IS_LOCKED_COL = "usgr_is_locked"
    USER_GEAR_SPECIAL_VALUE_COL = "usgr_special"
    CREATE_USER_GEAR_TABLE = f"""
    CREATE TABLE if not exists {USER_GEAR_TABLE} (
        {USER_GEAR_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT,
        {USER_GEAR_GUILD_ID_COL} INTEGER,
        {USER_GEAR_MEMBER_ID_COL} INTEGER,
        {USER_GEAR_NAME_COL} TEXT,
        {USER_GEAR_BASE_TYPE_COL} TEXT,
        {USER_GEAR_TYPE_COL} TEXT,
        {USER_GEAR_LEVEL_COL} INTEGER,
        {USER_GEAR_RARITY_COL} TEXT,
        {USER_GEAR_GENERATOR_VERSION_COL} TEXT,
        {USER_GEAR_IS_SCRAPPED_COL} INTEGER,
        {USER_GEAR_IS_LOCKED_COL} INTEGER,
        {USER_GEAR_SPECIAL_VALUE_COL} TEXT
    );"""

    USER_GEAR_MODIFIER_TABLE = "usergearmodifiers"
    USER_GEAR_MODIFIER_GEAR_ID_COL = "ugmo_gear_id"
    USER_GEAR_MODIFIER_TYPE_COL = "ugmo_type"
    USER_GEAR_MODIFIER_VALUE_COL = "ugmo_value"
    CREATE_USER_GEAR_MODIFIER_TABLE = f"""
    CREATE TABLE if not exists {USER_GEAR_MODIFIER_TABLE} (
        {USER_GEAR_MODIFIER_GEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_GEAR_MODIFIER_TYPE_COL} TEXT,
        {USER_GEAR_MODIFIER_VALUE_COL} REAL,
        PRIMARY KEY ({USER_GEAR_MODIFIER_GEAR_ID_COL}, {USER_GEAR_MODIFIER_TYPE_COL})
    );"""

    USER_GEAR_ENCHANTMENTS_TABLE = "usergearentchantments"
    USER_GEAR_ENCHANTMENTS_GEAR_ID_COL = "ugen_gear_id"
    USER_GEAR_ENCHANTMENTS_ID_COL = "ugen_id"
    CREATE_USER_GEAR_ENCHANTMENTS_TABLE = f"""
    CREATE TABLE if not exists {USER_GEAR_ENCHANTMENTS_TABLE } (
        {USER_GEAR_ENCHANTMENTS_GEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_GEAR_ENCHANTMENTS_ID_COL} INTEGER,
        PRIMARY KEY ({USER_GEAR_ENCHANTMENTS_GEAR_ID_COL}, {USER_GEAR_ENCHANTMENTS_ID_COL})
    );"""

    USER_GEAR_SKILL_TABLE = "usergearskills"
    USER_GEAR_SKILL_GEAR_ID_COL = "usk_gear_id"
    USER_GEAR_SKILL_TYPE_COL = "ugsk_type"
    CREATE_USER_GEAR_SKILL_TABLE = f"""
    CREATE TABLE if not exists {USER_GEAR_SKILL_TABLE} (
        {USER_GEAR_SKILL_GEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_GEAR_SKILL_TYPE_COL} TEXT,
        PRIMARY KEY ({USER_GEAR_SKILL_GEAR_ID_COL}, {USER_GEAR_SKILL_TYPE_COL})
    );"""

    USER_EQUIPMENT_TABLE = "userequipment"
    USER_EQUIPMENT_GUILD_ID_COL = "useq_guild_id"
    USER_EQUIPMENT_MEMBER_ID_COL = "useq_member_id"
    USER_EQUIPMENT_WEAPON_ID_COL = "useq_weapon_id"
    USER_EQUIPMENT_HEADGEAR_ID_COL = "useq_headgearr_id"
    USER_EQUIPMENT_BODYGEAR_ID_COL = "useq_bodygear_id"
    USER_EQUIPMENT_LEGGEAR_ID_COL = "useq_leggear_id"
    USER_EQUIPMENT_ACCESSORY_1_ID_COL = "useq_accessory_1_id"
    USER_EQUIPMENT_ACCESSORY_2_ID_COL = "useq_accessory_2_id"
    CREATE_USER_EQUIPMENT_TABLE = f"""
    CREATE TABLE if not exists {USER_EQUIPMENT_TABLE} (
        {USER_EQUIPMENT_GUILD_ID_COL} INTEGER,
        {USER_EQUIPMENT_MEMBER_ID_COL} INTEGER,
        {USER_EQUIPMENT_WEAPON_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_EQUIPMENT_HEADGEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_EQUIPMENT_BODYGEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_EQUIPMENT_LEGGEAR_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_EQUIPMENT_ACCESSORY_1_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        {USER_EQUIPMENT_ACCESSORY_2_ID_COL} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}),
        PRIMARY KEY ({USER_EQUIPMENT_GUILD_ID_COL}, {USER_EQUIPMENT_MEMBER_ID_COL})
    );"""

    USER_EQUIPPED_SKILLS_TABLE = "userequippedskills"
    USER_EQUIPPED_SKILLS_GUILD_ID_COL = "uses_guild_id"
    USER_EQUIPPED_SKILLS_MEMBER_ID_COL = "uses_member_id"
    USER_EQUIPPED_SKILLS_SKILL_ID_COL = "uses_skill_id"
    USER_EQUIPPED_SKILLS_SKILL_TYPE_COL = "uses_skill_type"
    USER_EQUIPPED_SKILLS_SLOT_COL = "uses_skill_slot"
    CREATE_USER_EQUIPPED_SKILLS_TABLE = f"""
    CREATE TABLE if not exists {USER_EQUIPPED_SKILLS_TABLE} (
        {USER_EQUIPPED_SKILLS_SKILL_ID_COL} INTEGER,
        {USER_EQUIPPED_SKILLS_GUILD_ID_COL} INTEGER,
        {USER_EQUIPPED_SKILLS_MEMBER_ID_COL} INTEGER,
        {USER_EQUIPPED_SKILLS_SKILL_TYPE_COL} TEXT,
        {USER_EQUIPPED_SKILLS_SLOT_COL} INTEGER,
        PRIMARY KEY ({USER_EQUIPPED_SKILLS_SKILL_ID_COL}, {USER_EQUIPPED_SKILLS_SLOT_COL})
    );"""

    COMBAT_EVENT_TABLE = "combatevents"
    COMBAT_EVENT_ID_COL = "cbev_id"
    COMBAT_EVENT_ENCOUNTER_ID_COL = "cbev_encounter_id"
    COMBAT_EVENT_MEMBER_ID = "cbev_member_id"
    COMBAT_EVENT_TARGET_ID = "cbev_target_id"
    COMBAT_EVENT_SKILL_TYPE = "cbev_skill_type"
    COMBAT_EVENT_SKILL_VALUE = "cbev_skill_value"
    COMBAT_EVENT_DISPLAY_VALUE = "cbev_display_value"
    COMBAT_EVENT_SKILL_ID = "cbev_skill_id"
    COMBAT_EVENT_TYPE_COL = "cbev_type"
    CREATE_COMBAT_EVENT_TABLE = f"""
    CREATE TABLE if not exists {COMBAT_EVENT_TABLE} (
        {COMBAT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {COMBAT_EVENT_ENCOUNTER_ID_COL} INTEGER REFERENCES {ENCOUNTER_TABLE} ({ENCOUNTER_ID_COL}), 
        {COMBAT_EVENT_MEMBER_ID} INTEGER, 
        {COMBAT_EVENT_TARGET_ID} INTEGER, 
        {COMBAT_EVENT_SKILL_TYPE} TEXT, 
        {COMBAT_EVENT_SKILL_VALUE} INTEGER, 
        {COMBAT_EVENT_DISPLAY_VALUE} INTEGER, 
        {COMBAT_EVENT_SKILL_ID} INTEGER REFERENCES {USER_GEAR_TABLE} ({USER_GEAR_ID_COL}), 
        {COMBAT_EVENT_TYPE_COL} TEXT, 
        PRIMARY KEY ({COMBAT_EVENT_ID_COL})
    );"""

    KARMA_EVENT_TABLE = "karmaevents"
    KARMA_EVENT_ID_COL = "kaev_id"
    KARMA_EVENT_RECIPIENT_ID = "kaev_recipient_id"
    KARMA_EVENT_GIVER_ID = "kaev_giver_id"
    KARMA_EVENT_AMOUNT = "kaev_amount"
    CREATE_KARMA_EVENT_TABLE = f"""
    CREATE TABLE if not exists {KARMA_EVENT_TABLE} (
        {KARMA_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {KARMA_EVENT_RECIPIENT_ID} INTEGER, 
        {KARMA_EVENT_GIVER_ID} INTEGER, 
        {KARMA_EVENT_AMOUNT} INTEGER, 
        PRIMARY KEY ({KARMA_EVENT_ID_COL})
    );"""

    STATUS_EFFECT_EVENT_TABLE = "statuseffectevents"
    STATUS_EFFECT_EVENT_ID_COL = "seev_id"
    STATUS_EFFECT_EVENT_ENCOUNTER_ID_COL = "seev_encounter_id"
    STATUS_EFFECT_EVENT_SOURCE_ID_COL = "seev_source_id"
    STATUS_EFFECT_EVENT_ACTOR_ID_COL = "seev_actor_id"
    STATUS_EFFECT_EVENT_STATUS_TYPE_COL = "seev_status_type"
    STATUS_EFFECT_EVENT_STACKS_COL = "seev_stacks"
    STATUS_EFFECT_EVENT_VALUE_COL = "seev_value"
    CREATE_STATUS_EFFECT_EVENT_TABLE = f"""
    CREATE TABLE if not exists {STATUS_EFFECT_EVENT_TABLE} (
        {STATUS_EFFECT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {STATUS_EFFECT_EVENT_ENCOUNTER_ID_COL} INTEGER, 
        {STATUS_EFFECT_EVENT_SOURCE_ID_COL} INTEGER, 
        {STATUS_EFFECT_EVENT_ACTOR_ID_COL} INTEGER, 
        {STATUS_EFFECT_EVENT_STATUS_TYPE_COL} TEXT, 
        {STATUS_EFFECT_EVENT_STACKS_COL} INTEGER,
        {STATUS_EFFECT_EVENT_VALUE_COL} REAL,
        PRIMARY KEY ({STATUS_EFFECT_EVENT_ID_COL})
    );"""

    EQUIPMENT_EVENT_TABLE = "equipmentevents"
    EQUIPMENT_EVENT_ID_COL = "eqev_id"
    EQUIPMENT_EVENT_MEMBER_ID = "eqev_member_id"
    EQUIPMENT_EVENT_EQUIPMENT_EVENT_TYPE = "eqev_type"
    EQUIPMENT_EVENT_ITEM_ID = "eqev_item_id"
    CREATE_EQUIPMENT_EVENT_TABLE = f"""
    CREATE TABLE if not exists {EQUIPMENT_EVENT_TABLE} (
        {EQUIPMENT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {EQUIPMENT_EVENT_MEMBER_ID} INTEGER, 
        {EQUIPMENT_EVENT_EQUIPMENT_EVENT_TYPE} TEST, 
        {EQUIPMENT_EVENT_ITEM_ID} INTEGER, 
        PRIMARY KEY ({EQUIPMENT_EVENT_ID_COL})
    );"""

    USER_SETTINGS_TABLE = "usersettings"
    USER_SETTINGS_GUILD_ID_COL = "usrs_guild_id"
    USER_SETTINGS_MEMBER_ID_COL = "usrs_member_id"
    USER_SETTINGS_SETTING_ID_COL = "usrs_setting_id"
    USER_SETTINGS_VALUE_COL = "usrs_value"
    CREATE_USER_SETTINGS_TABLE = f"""
    CREATE TABLE if not exists {USER_SETTINGS_TABLE} (
        {USER_SETTINGS_MEMBER_ID_COL} INTEGER,
        {USER_SETTINGS_GUILD_ID_COL} INTEGER,
        {USER_SETTINGS_SETTING_ID_COL} INTEGER,
        {USER_SETTINGS_VALUE_COL} TEXT,
        PRIMARY KEY ({USER_SETTINGS_MEMBER_ID_COL}, {USER_SETTINGS_GUILD_ID_COL}, {USER_SETTINGS_SETTING_ID_COL})
    );"""

    USER_SETTINGS_TABLE = "usersettings"
    USER_SETTINGS_GUILD_ID_COL = "usrs_guild_id"
    USER_SETTINGS_MEMBER_ID_COL = "usrs_member_id"
    USER_SETTINGS_SETTING_ID_COL = "usrs_setting_id"
    USER_SETTINGS_VALUE_COL = "usrs_value"
    CREATE_USER_SETTINGS_TABLE = f"""
    CREATE TABLE if not exists {USER_SETTINGS_TABLE} (
        {USER_SETTINGS_MEMBER_ID_COL} INTEGER,
        {USER_SETTINGS_GUILD_ID_COL} INTEGER,
        {USER_SETTINGS_SETTING_ID_COL} INTEGER,
        {USER_SETTINGS_VALUE_COL} TEXT,
        PRIMARY KEY ({USER_SETTINGS_MEMBER_ID_COL}, {USER_SETTINGS_GUILD_ID_COL}, {USER_SETTINGS_SETTING_ID_COL})
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
            await db.execute(self.CREATE_CURRENT_GUILD_SEASON_TABLE)
            await db.execute(self.CREATE_GUILD_SEASON_TABLE)
            await db.execute(self.CREATE_ENCOUNTER_TABLE)
            await db.execute(self.CREATE_ENCOUNTER_EVENT_TABLE)
            await db.execute(self.CREATE_COMBAT_EVENT_TABLE)
            await db.execute(self.CREATE_ENCOUNTER_THREAD_TABLE)
            await db.execute(self.CREATE_USER_GEAR_TABLE)
            await db.execute(self.CREATE_USER_GEAR_MODIFIER_TABLE)
            await db.execute(self.CREATE_USER_GEAR_ENCHANTMENTS_TABLE)
            await db.execute(self.CREATE_USER_GEAR_SKILL_TABLE)
            await db.execute(self.CREATE_USER_EQUIPMENT_TABLE)
            await db.execute(self.CREATE_USER_EQUIPPED_SKILLS_TABLE)
            await db.execute(self.CREATE_KARMA_EVENT_TABLE)
            await db.execute(self.CREATE_STATUS_EFFECT_EVENT_TABLE)
            await db.execute(self.CREATE_EQUIPMENT_EVENT_TABLE)
            await db.execute(self.CREATE_USER_SETTINGS_TABLE)
            await db.commit()
            self.logger.log(
                "DB", f"Loaded DB version {aiosqlite.__version__} from {self.db_file}."
            )

    async def __get_season_interval(self, guild_id: int, season_nr: int = None):
        start_timestamp = 0
        now = int(datetime.datetime.now().timestamp())

        if season_nr is None:
            start_timestamp = await self.get_guild_current_season_start(guild_id)
            end_timestamp = now
            return start_timestamp, end_timestamp

        prev_season = season_nr - 1
        if prev_season > 0:
            start_timestamp = await self.get_guild_season_end(guild_id, prev_season)

        end_timestamp = await self.get_guild_season_end(guild_id, season_nr)
        if end_timestamp == 0:
            end_timestamp = now

        return start_timestamp, end_timestamp

    async def __query_select(self, query: str, task=None):
        async with aiosqlite.connect(self.db_file, timeout=30) as db:  # noqa: SIM117
            async with db.execute(query, task) as cursor:
                rows = await cursor.fetchall()
                headings = [x[0] for x in cursor.description]
                return self.__parse_rows(rows, headings)

    async def __query_insert(self, query: str, task=None) -> int:
        async with aiosqlite.connect(self.db_file, timeout=30) as db:
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
        return "(" + ",".join(["?" for _ in range(len(attribute_list))]) + ")"

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

    async def __create_batch_base_event(self, event: BotEvent) -> int:
        command = f"""
                INSERT INTO {self.EVENT_TABLE} (
                {self.EVENT_TIMESTAMP_COL}, 
                {self.EVENT_GUILD_ID_COL}, 
                {self.EVENT_TYPE_COL}) 
                VALUES 
            """
        timestamp = event.get_timestamp()

        for i in range(event.amount):
            last = i + 1 == event.amount
            end = "," if not last else ";"
            command += (
                f"({timestamp}, {event.guild_id}, '{event.base_type.value}'){end}"
            )

        return await self.__query_insert(command)

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

    async def __create_batch_inventory_event(
        self, event_id: int, event: InventoryBatchEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.INVENTORY_EVENT_TABLE} (
            {self.INVENTORY_EVENT_ID_COL},
            {self.INVENTORY_EVENT_MEMBER_COL},
            {self.INVENTORY_EVENT_ITEM_TYPE_COL},
            {self.INVENTORY_EVENT_AMOUNT_COL})
            VALUES 
            """

        event_id = event_id - event.amount + 1
        for index, (amount, item) in enumerate(event.items):
            last = index + 1 == len(event.items)
            end = "," if not last else ";"
            command += f"({event_id}, {event.member_id}, '{item.value}', {amount}){end}"

            event_id += 1

        return await self.__query_insert(command)

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

    async def __create_encounter_event(
        self, event_id: int, event: EncounterEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.ENCOUNTER_EVENT_TABLE} (
            {self.ENCOUNTER_EVENT_ID_COL},
            {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL},
            {self.ENCOUNTER_EVENT_MEMBER_ID},
            {self.ENCOUNTER_EVENT_TYPE_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.encounter_id,
            event.member_id,
            event.encounter_event_type,
        )

        return await self.__query_insert(command, task)

    async def __create_combat_event(self, event_id: int, event: CombatEvent) -> int:
        command = f"""
            INSERT INTO {self.COMBAT_EVENT_TABLE} (
            {self.COMBAT_EVENT_ID_COL},
            {self.COMBAT_EVENT_ENCOUNTER_ID_COL},
            {self.COMBAT_EVENT_MEMBER_ID},
            {self.COMBAT_EVENT_TARGET_ID},
            {self.COMBAT_EVENT_SKILL_TYPE},
            {self.COMBAT_EVENT_SKILL_VALUE},
            {self.COMBAT_EVENT_DISPLAY_VALUE},
            {self.COMBAT_EVENT_SKILL_ID},
            {self.COMBAT_EVENT_TYPE_COL})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            event_id,
            event.encounter_id,
            event.member_id,
            event.target_id,
            event.skill_type,
            event.skill_value,
            event.display_value,
            event.skill_id,
            event.combat_event_type,
        )

        return await self.__query_insert(command, task)

    async def __create_karma_event(self, event_id: int, event: KarmaEvent) -> int:
        command = f"""
            INSERT INTO {self.KARMA_EVENT_TABLE} (
            {self.KARMA_EVENT_ID_COL},
            {self.KARMA_EVENT_RECIPIENT_ID},
            {self.KARMA_EVENT_GIVER_ID},
            {self.KARMA_EVENT_AMOUNT})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.recipient_id,
            event.giver_id,
            event.amount,
        )

        return await self.__query_insert(command, task)

    async def __create_status_effect_event(
        self, event_id: int, event: StatusEffectEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.STATUS_EFFECT_EVENT_TABLE} (
            {self.STATUS_EFFECT_EVENT_ID_COL},
            {self.STATUS_EFFECT_EVENT_ENCOUNTER_ID_COL},
            {self.STATUS_EFFECT_EVENT_SOURCE_ID_COL},
            {self.STATUS_EFFECT_EVENT_ACTOR_ID_COL},
            {self.STATUS_EFFECT_EVENT_STATUS_TYPE_COL},
            {self.STATUS_EFFECT_EVENT_STACKS_COL},
            {self.STATUS_EFFECT_EVENT_VALUE_COL})
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            event_id,
            event.encounter_id,
            event.source_id,
            event.actor_id,
            event.status_type,
            event.stacks,
            event.value,
        )

        return await self.__query_insert(command, task)

    async def __create_equipment_event(
        self, event_id: int, event: EquipmentEvent
    ) -> int:
        command = f"""
            INSERT INTO {self.EQUIPMENT_EVENT_TABLE} (
            {self.EQUIPMENT_EVENT_ID_COL},
            {self.EQUIPMENT_EVENT_MEMBER_ID},
            {self.EQUIPMENT_EVENT_EQUIPMENT_EVENT_TYPE},
            {self.EQUIPMENT_EVENT_ITEM_ID})
            VALUES (?, ?, ?, ?);
        """
        task = (
            event_id,
            event.member_id,
            event.equipment_event_type.value,
            event.item_id,
        )

        return await self.__query_insert(command, task)

    async def log_event(self, event: BotEvent) -> int:
        if event.type == EventType.INVENTORYBATCH:
            event_id = await self.__create_batch_base_event(event)
        else:
            event_id = await self.__create_base_event(event)

        if event_id is None:
            self.logger.error("DB", "Event creation error, id was NoneType")
            return None

        match event.type:
            case EventType.INTERACTION:
                await self.__create_interaction_event(event_id, event)
            case EventType.JAIL:
                await self.__create_jail_event(event_id, event)
            case EventType.TIMEOUT:
                await self.__create_timeout_event(event_id, event)
            case EventType.QUOTE:
                await self.__create_quote_event(event_id, event)
            case EventType.SPAM:
                await self.__create_spam_event(event_id, event)
            case EventType.BEANS:
                await self.__create_beans_event(event_id, event)
            case EventType.INVENTORY:
                await self.__create_inventory_event(event_id, event)
            case EventType.INVENTORYBATCH:
                await self.__create_batch_inventory_event(event_id, event)
            case EventType.LOOTBOX:
                await self.__create_loot_box_event(event_id, event)
            case EventType.BAT:
                await self.__create_bat_event(event_id, event)
            case EventType.PREDICTION:
                await self.__create_prediction_event(event_id, event)
            case EventType.GARDEN:
                await self.__create_garden_event(event_id, event)
            case EventType.ENCOUNTER:
                await self.__create_encounter_event(event_id, event)
            case EventType.COMBAT:
                await self.__create_combat_event(event_id, event)
            case EventType.STATUS_EFFECT:
                await self.__create_status_effect_event(event_id, event)
            case EventType.KARMA:
                await self.__create_karma_event(event_id, event)
            case EventType.EQUIPMENT:
                await self.__create_equipment_event(event_id, event)

        return event_id

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

    async def log_encounter(self, encounter: Encounter) -> int:
        command = f"""
            INSERT INTO {self.ENCOUNTER_TABLE} (
            {self.ENCOUNTER_GUILD_ID_COL},
            {self.ENCOUNTER_ENEMY_TYPE_COL},
            {self.ENCOUNTER_ENEMY_LEVEL_COL},
            {self.ENCOUNTER_ENEMY_HEALTH_COL},
            {self.ENCOUNTER_MESSAGE_ID_COL},
            {self.ENCOUNTER_CHANNEL_ID_COL},
            {self.ENCOUNTER_OWNER_ID_COL})
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            encounter.guild_id,
            encounter.enemy_type.value,
            encounter.enemy_level,
            encounter.max_hp,
            encounter.message_id,
            encounter.channel_id,
            encounter.owner_id,
        )

        return await self.__query_insert(command, task)

    async def log_encounter_thread(
        self, encounter_id: int, thread_id: int, guild_id: int, channel_id: int
    ) -> int:
        command = f"""
            INSERT INTO {self.ENCOUNTER_THREAD_TABLE} (
            {self.ENCOUNTER_THREAD_ID_COL},
            {self.ENCOUNTER_THREAD_ENCOUNTER_ID_COL},
            {self.ENCOUNTER_THREAD_GUILD_ID_COL},
            {self.ENCOUNTER_THREAD_CHANNEL_ID_COL})
            VALUES (?, ?, ?, ?);
        """
        task = (
            thread_id,
            encounter_id,
            guild_id,
            channel_id,
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
        self, guild_id: int, jail_id: int, season: int = None
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, user_id: int, season: int = None
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, user_id: int, season: int = None
    ) -> list[JailEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(None, season)
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
        self, guild_id: int, season: int = None
    ) -> dict[UserJail, list[JailEvent]]:
        jails = await self.get_jails_by_guild(guild_id)
        output = {}
        for jail in jails:
            output[jail] = await self.get_jail_events_by_jail(guild_id, jail.id, season)

        return output

    async def get_timeout_events_by_user(
        self, user_id: int, season: int = None
    ) -> list[TimeoutEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(None, season)
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
        self, guild_id: int, season: int = None
    ) -> list[TimeoutEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, user_id: int, season: int = None
    ) -> list[SpamEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(None, season)
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
        self, guild_id: int, season: int = None
    ) -> list[SpamEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, user_id: int, season: int = None
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(None, season)
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
        self, user_id: int, season: int = None
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(None, season)
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
        season: int = None,
    ) -> list[InteractionEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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

    async def get_last_loot_box_drop(self, guild_id: int) -> LootBox:
        command = f""" 
            SELECT * FROM {self.LOOTBOX_TABLE} 
            INNER JOIN {self.LOOTBOX_EVENT_TABLE} ON {self.LOOTBOX_ID_COL} = {self.LOOTBOX_EVENT_LOOTBOX_ID_COL}
            WHERE {self.LOOTBOX_GUILD_COL} = ?
            AND {self.LOOTBOX_EVENT_TYPE_COL} = ?
            ORDER BY {self.LOOTBOX_ID_COL} DESC
            LIMIT 1;
        """
        task = (guild_id, LootBoxEventType.DROP.value)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        items = await self.get_lootbox_items(rows[0][self.LOOTBOX_ID_COL])

        return LootBox.from_db_row(rows[0], items)

    async def get_loot_box_events_by_lootbox(
        self,
        lootbox_id: int,
    ) -> list[LootBoxEvent]:
        command = f"""
            SELECT * FROM {self.LOOTBOX_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            WHERE {self.LOOTBOX_EVENT_LOOTBOX_ID_COL} = {int(lootbox_id)}
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC;
        """
        rows = await self.__query_select(command)
        if not rows:
            return []
        return [LootBoxEvent.from_db_row(row) for row in rows]

    async def get_member_beans(
        self, guild_id: int, user_id: int, season: int = None
    ) -> int:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, season: int = None
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, season: int = None
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, season: int = None
    ) -> dict[int, int]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, member_id: int, season: int = None
    ) -> int:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, until: int = None, season: int = None
    ) -> dict[int, int]:
        start_timestamp, _ = await self.__get_season_interval(guild_id, season)
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
        season: int = None,
    ) -> BeansEvent:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, season: int = None
    ) -> dict[int, dict[ItemType, int]]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
            if row[self.INVENTORY_EVENT_ITEM_TYPE_COL] not in ItemType:
                continue
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
        season: int = None,
        item_types: list[ItemType] = None,
    ) -> dict[ItemType, int]:
        item_types_filter = ""

        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
            and row[self.INVENTORY_EVENT_ITEM_TYPE_COL] in ItemType
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
        self, predictions: list[Prediction] | None
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
        season: int = None,
    ) -> BatEvent:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, season: int = None
    ) -> list[tuple[int, LootBox]]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )

        lootbox_types = [LootBoxEventType.CLAIM.value, LootBoxEventType.OPEN.value]
        list_sanitized = self.__list_sanitizer(lootbox_types)

        command = f"""
            SELECT * FROM {self.LOOTBOX_TABLE}
            INNER JOIN {self.LOOTBOX_EVENT_TABLE} ON {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_LOOTBOX_ID_COL} = {self.LOOTBOX_TABLE}.{self.LOOTBOX_ID_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
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
                    row, (await self.get_lootbox_items(row[self.LOOTBOX_ID_COL]))
                ),
            )
            for row in rows
        ]

    async def get_guild_beans_events(
        self,
        guild_id: int,
        event_types: list[BeansEventType],
        season: int = None,
    ) -> list[BeansEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, garden_id: int, season: int = None
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

        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )
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
        self, guild_id: int, user_id: int, season: int = None
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
        self, guild_id: int, user_id: int, season: int = None
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

        plots = await self.get_garden_plots(guild_id, garden_id, season)
        user_seeds = await self.get_user_seeds(guild_id, user_id, season=season)

        return UserGarden(
            garden_id,
            guild_id,
            user_id,
            plots,
            user_seeds,
        )

    async def get_guild_gardens(
        self, guild_id: int, season: int = None
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

            plots = await self.get_garden_plots(guild_id, garden_id, season)

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

    async def get_guild_level(self, guild_id: int) -> int:
        command = f"""
            INSERT OR IGNORE INTO {self.GUILD_CURRENT_SEASON_TABLE}
            ({self.GUILD_CURRENT_SEASON_GUILD_ID_COL}, {self.GUILD_CURRENT_SEASON_GUILD_LEVEL_COL}) 
            VALUES(?, ?);
        """
        task = (guild_id, 1)

        await self.__query_insert(command, task)

        command = f""" 
            SELECT * FROM {self.GUILD_CURRENT_SEASON_TABLE} 
            WHERE {self.GUILD_CURRENT_SEASON_GUILD_ID_COL} = {int(guild_id)}
            LIMIT 1;
        """
        rows = await self.__query_select(command)
        if not rows:
            return 1

        return int(rows[0][self.GUILD_CURRENT_SEASON_GUILD_LEVEL_COL])

    async def get_forge_level(self, guild_id: int) -> int:
        guild_level = await self.get_guild_level(guild_id)

        progress = await self.get_guild_current_level_kills(guild_id, guild_level)
        if progress < Config.FORGE_UNLOCK_REQUIREMENT:
            return max(1, guild_level - 1)
        return guild_level

    async def set_guild_level(self, guild_id: int, level: int) -> int:
        command = f""" 
            UPDATE {self.GUILD_CURRENT_SEASON_TABLE} 
            SET {self.GUILD_CURRENT_SEASON_GUILD_LEVEL_COL} = ?
            WHERE {self.GUILD_CURRENT_SEASON_GUILD_ID_COL} = ?
        """
        task = (level, guild_id)
        return await self.__query_insert(command, task)

    async def get_guild_current_level_kills(
        self, guild_id: int, guild_level: int, start_id: int | None = None
    ) -> tuple[int, int]:
        if start_id is None:
            start_id = 0

        command = f""" 
            SELECT COUNT(*) as progress FROM {self.ENCOUNTER_TABLE} 
            INNER JOIN {self.ENCOUNTER_EVENT_TABLE} ON {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = {self.ENCOUNTER_ID_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.ENCOUNTER_ENEMY_LEVEL_COL} = ?
            AND {self.ENCOUNTER_EVENT_TYPE_COL} = ?
            AND {self.ENCOUNTER_GUILD_ID_COL} = ?
            AND {self.EVENT_ID_COL} > ?
            GROUP BY {self.ENCOUNTER_GUILD_ID_COL}
            ;
        """
        task = (guild_level, EncounterEventType.ENEMY_DEFEAT, guild_id, start_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return 0

        return int(rows[0]["progress"])

    async def get_guild_level_progress(
        self, guild_id: int, guild_level: int
    ) -> tuple[int, int]:
        start_id = 0
        requirement = Config.LEVEL_REQUIREMENTS[guild_level]

        boss_types = {
            3: EnemyType.DADDY_P1,
            6: EnemyType.WEEB_BALL,
            # 9: None,
            # 12: None,
        }

        if guild_level in Config.BOSS_LEVELS:
            last_fight_event = await self.get_guild_last_boss_attempt(
                guild_id, boss_types[guild_level]
            )
            if last_fight_event is not None:
                start_id = last_fight_event.id
                requirement = Config.BOSS_RETRY_REQUIREMENT

        progress = await self.get_guild_current_level_kills(
            guild_id, guild_level, start_id
        )

        return progress, requirement

    async def get_guild_last_boss_attempt(
        self, guild_id: int, enemy_type: EnemyType
    ) -> EncounterEvent:
        command = f""" 
            SELECT * FROM {self.ENCOUNTER_TABLE} 
            INNER JOIN {self.ENCOUNTER_EVENT_TABLE} ON {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = {self.ENCOUNTER_ID_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.ENCOUNTER_ENEMY_TYPE_COL} = ?
            AND {self.ENCOUNTER_EVENT_TYPE_COL} = ?
            AND {self.ENCOUNTER_GUILD_ID_COL} = ?
            ORDER BY {self.EVENT_ID_COL} DESC
            LIMIT 1
            ;
        """
        task = (enemy_type.value, EncounterEventType.END, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        return EncounterEvent.from_db_row(rows[0])

    async def get_encounter_by_encounter_id(self, encounter_id: int) -> Encounter:
        command = f""" 
            SELECT * FROM {self.ENCOUNTER_TABLE} 
            WHERE {self.ENCOUNTER_ID_COL} = {int(encounter_id)}
            LIMIT 1;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None

        return Encounter.from_db_row(rows[0])

    async def get_encounter_by_thread_id(
        self, guild_id: int, channel_id: int
    ) -> Encounter | None:
        command = f""" 
            SELECT * FROM {self.ENCOUNTER_TABLE} 
            INNER JOIN {self.ENCOUNTER_THREAD_TABLE} 
            ON {self.ENCOUNTER_ID_COL} = {self.ENCOUNTER_THREAD_ENCOUNTER_ID_COL}
            WHERE {self.ENCOUNTER_THREAD_ID_COL} = ?
            AND {self.ENCOUNTER_GUILD_ID_COL} = ?
            LIMIT 1;
        """
        task = (channel_id, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        return Encounter.from_db_row(rows[0])

    async def get_encounter_by_message_id(
        self, guild_id: int, message_id: int
    ) -> Encounter:
        command = f""" 
            SELECT * FROM {self.ENCOUNTER_TABLE} 
            WHERE {self.ENCOUNTER_MESSAGE_ID_COL} = ?
            AND {self.ENCOUNTER_GUILD_ID_COL} = ?
            LIMIT 1;
        """
        task = (message_id, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        return Encounter.from_db_row(rows[0])

    async def get_active_encounters(self, guild_id: int) -> list[int]:
        start_timestamp = await self.get_guild_current_season_start(guild_id)

        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND  {self.ENCOUNTER_EVENT_TYPE_COL} in (? ,?)
            AND {self.EVENT_TIMESTAMP_COL} > ?;
        """
        task = (
            guild_id,
            EncounterEventType.SPAWN.value,
            EncounterEventType.END.value,
            start_timestamp,
        )
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        started_encounters = []
        ended_encounters = []
        for row in rows:
            match EncounterEventType(row[self.ENCOUNTER_EVENT_TYPE_COL]):
                case EncounterEventType.SPAWN:
                    started_encounters.append(
                        row[self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL]
                    )
                case EncounterEventType.END:
                    ended_encounters.append(row[self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL])

        active_encounters = []
        for encounter_id in started_encounters:
            if encounter_id not in ended_encounters:
                active_encounters.append(encounter_id)
        return active_encounters

    async def get_inactive_encounter_participants(
        self, guild_id: int
    ) -> dict[int, list[int]]:
        active_encounters = await self.get_active_encounters(guild_id)

        if len(active_encounters) <= 0:
            return {}

        list_sanitized = self.__list_sanitizer(active_encounters)
        participants = {}

        for encounter_id in active_encounters:
            participants[encounter_id] = []

        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND  {self.ENCOUNTER_EVENT_TYPE_COL} = ?
            AND  {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} IN {list_sanitized};
        """

        task = (
            guild_id,
            EncounterEventType.MEMBER_OUT.value,
            *active_encounters,
        )

        rows = await self.__query_select(command, task)
        if not rows:
            return participants

        for row in rows:
            encounter_id = row[self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL]
            member_id = row[self.ENCOUNTER_EVENT_MEMBER_ID]
            participants[encounter_id].append(member_id)

        return participants

    async def get_encounter_participants(self, guild_id: int) -> dict[int, list[int]]:
        active_encounters = await self.get_active_encounters(guild_id)

        if len(active_encounters) <= 0:
            return {}

        list_sanitized = self.__list_sanitizer(active_encounters)
        participants = {}

        for encounter_id in active_encounters:
            participants[encounter_id] = []

        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND  {self.ENCOUNTER_EVENT_TYPE_COL} IN (?, ?)
            AND  {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} IN {list_sanitized}
            ORDER BY {self.ENCOUNTER_EVENT_ID_COL} ASC;
        """

        task = (
            guild_id,
            EncounterEventType.MEMBER_ENGAGE.value,
            EncounterEventType.MEMBER_DISENGAGE.value,
            *active_encounters,
        )
        rows = await self.__query_select(command, task)
        if not rows:
            return participants

        for row in rows:
            encounter_id = row[self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL]
            member_id = row[self.ENCOUNTER_EVENT_MEMBER_ID]
            if row[self.ENCOUNTER_EVENT_TYPE_COL] == EncounterEventType.MEMBER_ENGAGE:
                participants[encounter_id].append(member_id)
            else:
                participants[encounter_id].remove(member_id)

        return participants

    async def get_encounter_out_participants_by_encounter_id(
        self, encounter_id: int
    ) -> list[int]:
        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE  {self.ENCOUNTER_EVENT_TYPE_COL} = ?
            AND  {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = ?;
        """

        task = (
            EncounterEventType.MEMBER_OUT.value,
            encounter_id,
        )
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        participants = []
        for row in rows:
            member_id = row[self.ENCOUNTER_EVENT_MEMBER_ID]
            participants.append(member_id)

        return participants

    async def get_encounter_participants_by_encounter_id(
        self, encounter_id: int
    ) -> list[int]:
        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE  {self.ENCOUNTER_EVENT_TYPE_COL} IN (?, ?)
            AND  {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = ?
            ORDER BY {self.ENCOUNTER_EVENT_ID_COL} ASC;
        """

        task = (
            EncounterEventType.MEMBER_ENGAGE.value,
            EncounterEventType.MEMBER_DISENGAGE.value,
            encounter_id,
        )
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        participants = []
        for row in rows:
            member_id = row[self.ENCOUNTER_EVENT_MEMBER_ID]
            if row[self.ENCOUNTER_EVENT_TYPE_COL] == EncounterEventType.MEMBER_ENGAGE:
                participants.append(member_id)
            else:
                participants.remove(member_id)

        return participants

    async def get_last_encounter_spawn_event(
        self, guild_id: int, min_lvl: int = None, max_lvl: int = None
    ) -> EncounterEvent:
        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            INNER JOIN {self.ENCOUNTER_TABLE} ON {self.ENCOUNTER_TABLE}.{self.ENCOUNTER_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND  {self.ENCOUNTER_EVENT_TYPE_COL} = ?
        """

        task = [guild_id, EncounterEventType.SPAWN.value]

        if min_lvl is not None:
            command += f"""
                AND  {self.ENCOUNTER_ENEMY_LEVEL_COL} >= ?
            """
            task.append(min_lvl)

        if max_lvl is not None:
            command += f"""
                AND  {self.ENCOUNTER_ENEMY_LEVEL_COL} <= ?
            """
            task.append(max_lvl)

        command += f"""
            ORDER BY {self.EVENT_ID_COL} DESC
        """

        task = tuple(task)
        rows = await self.__query_select(command, task)
        if not rows:
            return None

        return EncounterEvent.from_db_row(rows[0])

    async def get_encounter_thread(self, encounter_id: int) -> int:
        command = f""" 
            SELECT * FROM {self.ENCOUNTER_THREAD_TABLE} 
            WHERE {self.ENCOUNTER_THREAD_ENCOUNTER_ID_COL} = {int(encounter_id)}
            LIMIT 1;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None

        return int(rows[0][self.ENCOUNTER_THREAD_ID_COL])

    async def get_encounter_events_by_encounter_id(
        self, encounter_id: int
    ) -> list[EncounterEvent]:
        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            WHERE {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = {int(encounter_id)}
            ORDER BY {self.EVENT_ID_COL} DESC;
        """
        rows = await self.__query_select(command)
        if not rows:
            return []

        return [EncounterEvent.from_db_row(row) for row in rows]

    async def get_encounter_events(
        self,
        guild_id: int,
        enemy_types: list[EnemyType],
        event_types: list[EncounterEventType],
    ) -> list[tuple[EncounterEvent, EnemyType]]:
        enemy_list_sanitized = self.__list_sanitizer(enemy_types)
        event_type_list_sanitized = self.__list_sanitizer(event_types)

        command = f"""
            SELECT * FROM {self.ENCOUNTER_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.ENCOUNTER_EVENT_TABLE}.{self.ENCOUNTER_EVENT_ID_COL}
            INNER JOIN {self.ENCOUNTER_TABLE} ON {self.ENCOUNTER_EVENT_ENCOUNTER_ID_COL} = {self.ENCOUNTER_ID_COL}
            WHERE {self.ENCOUNTER_ENEMY_TYPE_COL} in {enemy_list_sanitized}
            AND {self.ENCOUNTER_EVENT_TYPE_COL} in {event_type_list_sanitized}
            AND {self.ENCOUNTER_GUILD_ID_COL} = ?
            ORDER BY {self.EVENT_ID_COL} DESC;
        """

        task = (*enemy_types, *event_types, guild_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        return [
            (
                EncounterEvent.from_db_row(row),
                EnemyType(row[self.ENCOUNTER_ENEMY_TYPE_COL]),
            )
            for row in rows
        ]

    async def get_combat_events_by_encounter_id(
        self, encounter_id: int
    ) -> list[CombatEvent]:
        command = f"""
            SELECT * FROM {self.COMBAT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.COMBAT_EVENT_TABLE}.{self.COMBAT_EVENT_ID_COL}
            WHERE {self.COMBAT_EVENT_ENCOUNTER_ID_COL} = {int(encounter_id)}
            ORDER BY {self.EVENT_ID_COL} DESC;
        """
        rows = await self.__query_select(command)
        if not rows:
            return []

        return [CombatEvent.from_db_row(row) for row in rows]

    async def log_user_gear_modifiers(self, gear_id: int, gear: Gear):
        command = f"""
            INSERT INTO {self.USER_GEAR_MODIFIER_TABLE} (
            {self.USER_GEAR_MODIFIER_GEAR_ID_COL},
            {self.USER_GEAR_MODIFIER_TYPE_COL},
            {self.USER_GEAR_MODIFIER_VALUE_COL})
            VALUES (?, ?, ?);
        """

        for modifier, value in gear.modifiers.items():
            task = (
                gear_id,
                modifier.value,
                value,
            )
            await self.__query_insert(command, task)

    async def delete_user_gear_modifiers(self, gear_id: int):
        command = f"""
            DELETE FROM {self.USER_GEAR_MODIFIER_TABLE}
            WHERE {self.USER_GEAR_MODIFIER_GEAR_ID_COL} = {int(gear_id)}
        """

        return await self.__query_insert(command)

    async def log_user_gear_skills(self, gear_id: int, gear: Gear):
        command = f"""
            INSERT INTO {self.USER_GEAR_SKILL_TABLE} (
            {self.USER_GEAR_SKILL_GEAR_ID_COL},
            {self.USER_GEAR_SKILL_TYPE_COL})
            VALUES (?, ?);
        """

        for skill_type in gear.skills:
            task = (
                gear_id,
                skill_type.value,
            )
            await self.__query_insert(command, task)

    async def log_user_drop(
        self,
        guild_id: int,
        member_id: int,
        drop: Droppable,
        generator_version: str,
    ):
        command = f"""
            INSERT INTO {self.USER_GEAR_TABLE} (
            {self.USER_GEAR_GUILD_ID_COL},
            {self.USER_GEAR_MEMBER_ID_COL},
            {self.USER_GEAR_BASE_TYPE_COL},
            {self.USER_GEAR_TYPE_COL},
            {self.USER_GEAR_LEVEL_COL},
            {self.USER_GEAR_RARITY_COL},
            {self.USER_GEAR_GENERATOR_VERSION_COL},
            {self.USER_GEAR_IS_SCRAPPED_COL},
            {self.USER_GEAR_IS_LOCKED_COL},
            {self.USER_GEAR_SPECIAL_VALUE_COL})
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        task = (
            guild_id,
            member_id,
            drop.base.base_type.value,
            drop.type.value,
            drop.level,
            drop.rarity.value,
            generator_version,
            0,
            0,
            drop.base.special,
        )

        insert_id = await self.__query_insert(command, task)

        if drop.base.base_type == Base.GEAR:
            gear: Gear = drop
            await self.log_user_gear_modifiers(insert_id, gear)
            await self.log_user_gear_skills(insert_id, gear)

        return insert_id

    async def get_skill_by_id(self, skill_id: int | None) -> Skill:
        if skill_id is None:
            return None

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            WHERE {self.USER_GEAR_ID_COL} = {int(skill_id)}
            ;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None

        id = rows[0][self.USER_GEAR_ID_COL]
        skill_type = SkillType(rows[0][self.USER_GEAR_TYPE_COL])
        base_class = globals()[skill_type]
        base_skill: BaseSkill = base_class()  # noqa: F405
        rarity = Rarity(rows[0][self.USER_GEAR_RARITY_COL])
        level = rows[0][self.USER_GEAR_LEVEL_COL]
        locked = int(rows[0][self.USER_GEAR_IS_LOCKED_COL]) == 1

        return Skill(
            base_skill=base_skill,
            rarity=rarity,
            level=level,
            locked=locked,
            id=id,
        )

    async def get_enchantment_by_id(
        self, enchantment_id: int | None
    ) -> Enchantment | EffectEnchantment:
        if enchantment_id is None:
            return None

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            WHERE {self.USER_GEAR_ID_COL} = {int(enchantment_id)}
            ;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None

        id = rows[0][self.USER_GEAR_ID_COL]
        enchantment_type = EnchantmentType(rows[0][self.USER_GEAR_TYPE_COL])
        base_class = globals()[enchantment_type]
        base_enchantment: BaseEnchantment = base_class()  # noqa: F405
        rarity = Rarity(rows[0][self.USER_GEAR_RARITY_COL])
        level = rows[0][self.USER_GEAR_LEVEL_COL]
        locked = int(rows[0][self.USER_GEAR_IS_LOCKED_COL]) == 1

        special = rows[0][self.USER_GEAR_SPECIAL_VALUE_COL]

        if base_enchantment.enchantment_effect == EnchantmentEffect.EFFECT:
            if special is not None:
                match enchantment_type:
                    case EnchantmentType.SKILL_STACKS:
                        skill_type = SkillType(special)
                        base_enchantment = SkillStacks(level, skill_type)  # noqa: F405

            return EffectEnchantment(
                base_enchantment=base_enchantment,
                rarity=rarity,
                level=level,
                locked=locked,
                id=id,
            )
        else:
            return Enchantment(
                base_enchantment=base_enchantment,
                rarity=rarity,
                level=level,
                locked=locked,
                id=id,
            )

    async def clear_user_gear_enchantment(self, gear_id: int):
        command = f"""
            DELETE FROM {self.USER_GEAR_ENCHANTMENTS_TABLE} 
            WHERE {self.USER_GEAR_ENCHANTMENTS_GEAR_ID_COL} = {int(gear_id)}
        """

        return await self.__query_insert(command)

    async def log_user_gear_enchantment(
        self, gear: Gear, enchantments: list[Enchantment]
    ) -> Gear:
        await self.clear_user_gear_enchantment(gear.id)
        await self.delete_gear_by_ids([enchantment.id for enchantment in enchantments])

        command = f"""
            INSERT INTO {self.USER_GEAR_ENCHANTMENTS_TABLE} (
            {self.USER_GEAR_ENCHANTMENTS_GEAR_ID_COL},
            {self.USER_GEAR_ENCHANTMENTS_ID_COL})
            VALUES (?, ?);
        """

        for enchantment in enchantments:
            task = (
                gear.id,
                enchantment.id,
            )
            await self.__query_insert(command, task)

        return await self.get_gear_by_id(gear.id)

    async def get_gear_by_id(self, gear_id: int | None) -> Gear:
        if gear_id is None:
            return None

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            LEFT JOIN {self.USER_GEAR_MODIFIER_TABLE} ON {self.USER_GEAR_MODIFIER_GEAR_ID_COL} = {self.USER_GEAR_ID_COL}
            LEFT JOIN {self.USER_GEAR_SKILL_TABLE} ON {self.USER_GEAR_SKILL_GEAR_ID_COL} = {self.USER_GEAR_ID_COL}
            LEFT JOIN {self.USER_GEAR_ENCHANTMENTS_TABLE} ON {self.USER_GEAR_ENCHANTMENTS_GEAR_ID_COL} = {self.USER_GEAR_ID_COL}
            WHERE {self.USER_GEAR_ID_COL} = {int(gear_id)}
            AND {self.USER_GEAR_IS_SCRAPPED_COL} = 0
            ;
        """
        rows = await self.__query_select(command)
        if not rows:
            return None

        id = rows[0][self.USER_GEAR_ID_COL]
        name = rows[0][self.USER_GEAR_NAME_COL]
        gear_base_type = GearBaseType(rows[0][self.USER_GEAR_TYPE_COL])
        base_class = globals()[gear_base_type]
        gear_base: GearBase = base_class()  # noqa: F405
        rarity = Rarity(rows[0][self.USER_GEAR_RARITY_COL])
        level = rows[0][self.USER_GEAR_LEVEL_COL]
        locked = int(rows[0][self.USER_GEAR_IS_LOCKED_COL]) == 1

        modifiers = {}
        enchantments = {}
        skills = []

        for row in rows:
            skill_name = row[self.USER_GEAR_SKILL_TYPE_COL]
            if skill_name is not None:
                skill_type = SkillType(skill_name)
                if skill_type not in skills:
                    skills.append(skill_type)

            modifier_name = row[self.USER_GEAR_MODIFIER_TYPE_COL]
            if modifier_name is not None:
                modifier_type = GearModifierType(modifier_name)
                if modifier_type not in modifiers:
                    modifiers[modifier_type] = row[self.USER_GEAR_MODIFIER_VALUE_COL]

            enchantment_id = row[self.USER_GEAR_ENCHANTMENTS_ID_COL]
            if enchantment_id is not None and enchantment_id not in enchantments:
                enchantment = await self.get_enchantment_by_id(enchantment_id)
                enchantment = await self.get_enchantment_by_id(enchantment_id)
                enchantments[enchantment_id] = enchantment

        return Gear(
            name=name,
            base=gear_base,
            rarity=rarity,
            level=level,
            modifiers=modifiers,
            skills=skills,
            enchantments=list(enchantments.values()),
            locked=locked,
            id=id,
        )

    async def delete_gear_by_ids(self, gear_ids: list[int]):
        if gear_ids is None or len(gear_ids) == 0:
            return

        list_sanitized = self.__list_sanitizer(gear_ids)

        command = f"""
            UPDATE {self.USER_GEAR_TABLE} SET
            {self.USER_GEAR_IS_SCRAPPED_COL} = 1
            WHERE {self.USER_GEAR_ID_COL} IN {list_sanitized};
        """
        task = gear_ids
        await self.__query_insert(command, task)

    async def update_lock_gear_by_id(self, gear_id: int | None, lock: bool):

        lock_value = 1 if lock else 0

        if gear_id is None:
            return
        command = f"""
            UPDATE {self.USER_GEAR_TABLE} SET
            {self.USER_GEAR_IS_LOCKED_COL} = ?
            WHERE {self.USER_GEAR_ID_COL} = ?;
        """
        task = (lock_value, gear_id)

        await self.__query_insert(command, task)

    async def update_gear_rarity(self, gear_id: int, rarity: Rarity):
        if gear_id is None:
            return
        command = f"""
            UPDATE {self.USER_GEAR_TABLE} SET
            {self.USER_GEAR_RARITY_COL} = ?
            WHERE {self.USER_GEAR_ID_COL} = ?;
        """
        task = (rarity.value, gear_id)

        await self.__query_insert(command, task)

    async def create_user_equipment(self, guild_id: int, user_id: int) -> int:
        command = f"""
            INSERT OR IGNORE INTO {self.USER_EQUIPMENT_TABLE}
            ({self.USER_EQUIPMENT_GUILD_ID_COL}, {self.USER_EQUIPMENT_MEMBER_ID_COL}) 
            VALUES(?, ?);
        """
        task = (guild_id, user_id)

        insert_id = await self.__query_insert(command, task)

        return insert_id

    async def get_user_active_enchantments(
        self, guild_id: int, member_id: int
    ) -> list[Enchantment]:

        command = f""" 
            SELECT * FROM {self.USER_GEAR_ENCHANTMENTS_TABLE} 
            INNER JOIN {self.USER_GEAR_TABLE} on {self.USER_GEAR_ID_COL} = {self.USER_GEAR_ENCHANTMENTS_GEAR_ID_COL}
            WHERE {self.USER_GEAR_GUILD_ID_COL} = ?
            AND {self.USER_GEAR_MEMBER_ID_COL} = ?
            ;
        """

        task = (guild_id, member_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        enchantments = []

        for row in rows:
            enchantment_id = row[self.USER_GEAR_ENCHANTMENTS_ID_COL]
            enchantment = await self.get_enchantment_by_id(enchantment_id)
            if enchantment is not None:
                enchantments.append(enchantment)

        return enchantments

    async def get_user_equipped_skills(
        self, guild_id: int, member_id: int
    ) -> dict[int, Skill]:
        command = f""" 
            SELECT * FROM {self.USER_EQUIPPED_SKILLS_TABLE} 
            WHERE {self.USER_EQUIPPED_SKILLS_GUILD_ID_COL} = ?
            AND {self.USER_EQUIPPED_SKILLS_MEMBER_ID_COL} = ?
            ;
        """

        skills = {}
        for index in range(4):
            skills[index] = None

        task = (guild_id, member_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return skills

        for row in rows:
            skill_id = row[self.USER_EQUIPPED_SKILLS_SKILL_ID_COL]
            slot = row[self.USER_EQUIPPED_SKILLS_SLOT_COL]
            skill = await self.get_skill_by_id(skill_id)
            if skill is not None:
                skills[slot] = skill

        return skills

    async def get_user_equipment_slot(
        self, guild_id: int, member_id: int, gear_slot: EquipmentSlot
    ) -> list[Gear]:
        await self.create_user_equipment(guild_id, member_id)

        command = f""" 
            SELECT * FROM {self.USER_EQUIPMENT_TABLE} 
            WHERE {self.USER_EQUIPMENT_GUILD_ID_COL} = ?
            AND {self.USER_EQUIPMENT_MEMBER_ID_COL} = ?
            LIMIT 1;
        """

        task = (guild_id, member_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        row = rows[0]

        equipped = []

        match gear_slot:
            case EquipmentSlot.WEAPON:
                gear = await self.get_gear_by_id(row[self.USER_EQUIPMENT_WEAPON_ID_COL])
                if gear is None:
                    if row[self.USER_EQUIPMENT_WEAPON_ID_COL] == -2:
                        gear = DefaultWand()
                    else:
                        gear = DefaultStick()
                equipped.append(gear)
            case EquipmentSlot.HEAD:
                gear = await self.get_gear_by_id(
                    row[self.USER_EQUIPMENT_HEADGEAR_ID_COL]
                )
                if gear is None:
                    gear = DefaultCap()
                equipped.append(gear)
            case EquipmentSlot.BODY:
                gear = await self.get_gear_by_id(
                    row[self.USER_EQUIPMENT_BODYGEAR_ID_COL]
                )
                if gear is None:
                    gear = DefaultShirt()
                equipped.append(gear)
            case EquipmentSlot.LEGS:
                gear = await self.get_gear_by_id(
                    row[self.USER_EQUIPMENT_LEGGEAR_ID_COL]
                )
                if gear is None:
                    gear = DefaultPants()
                equipped.append(gear)
            case EquipmentSlot.ACCESSORY:
                gear_1 = await self.get_gear_by_id(
                    row[self.USER_EQUIPMENT_ACCESSORY_1_ID_COL]
                )
                gear_2 = await self.get_gear_by_id(
                    row[self.USER_EQUIPMENT_ACCESSORY_2_ID_COL]
                )
                if gear_1 is not None:
                    equipped.append(gear_1)
                else:
                    equipped.append(DefaultAccessory1())

                if gear_2 is not None:
                    equipped.append(gear_2)
                else:
                    equipped.append(DefaultAccessory2())

        return equipped

    async def get_user_equipment(
        self, guild_id: int, member_id: int
    ) -> CharacterEquipment:
        await self.create_user_equipment(guild_id, member_id)

        command = f""" 
            SELECT * FROM {self.USER_EQUIPMENT_TABLE} 
            WHERE {self.USER_EQUIPMENT_GUILD_ID_COL} = ?
            AND {self.USER_EQUIPMENT_MEMBER_ID_COL} = ?
            LIMIT 1;
        """

        task = (guild_id, member_id)
        rows = await self.__query_select(command, task)
        if not rows:
            return None
        row = rows[0]

        weapon = None
        weapon_id = row[self.USER_EQUIPMENT_WEAPON_ID_COL]
        if weapon_id is not None and weapon_id < 0:
            match weapon_id:
                case -1:
                    weapon = DefaultStick()
                case -2:
                    weapon = DefaultWand()

        if weapon is None:
            weapon = await self.get_gear_by_id(weapon_id)

        head_gear = await self.get_gear_by_id(row[self.USER_EQUIPMENT_HEADGEAR_ID_COL])
        body_gear = await self.get_gear_by_id(row[self.USER_EQUIPMENT_BODYGEAR_ID_COL])
        leg_gear = await self.get_gear_by_id(row[self.USER_EQUIPMENT_LEGGEAR_ID_COL])
        accessory_1 = await self.get_gear_by_id(
            row[self.USER_EQUIPMENT_ACCESSORY_1_ID_COL]
        )
        accessory_2 = await self.get_gear_by_id(
            row[self.USER_EQUIPMENT_ACCESSORY_2_ID_COL]
        )

        level = await self.get_guild_level(guild_id)

        return CharacterEquipment(
            member_id=member_id,
            level=level,
            weapon=weapon,
            head_gear=head_gear,
            body_gear=body_gear,
            leg_gear=leg_gear,
            accessory_1=accessory_1,
            accessory_2=accessory_2,
        )

    async def update_user_equipment(
        self, guild_id: int, member_id: int, gear: Gear, acc_slot_2: bool = False
    ):
        await self.create_user_equipment(guild_id, member_id)

        column = ""

        if acc_slot_2:
            column = self.USER_EQUIPMENT_ACCESSORY_2_ID_COL
        else:
            match gear.base.slot:
                case EquipmentSlot.WEAPON:
                    column = self.USER_EQUIPMENT_WEAPON_ID_COL
                case EquipmentSlot.HEAD:
                    column = self.USER_EQUIPMENT_HEADGEAR_ID_COL
                case EquipmentSlot.BODY:
                    column = self.USER_EQUIPMENT_BODYGEAR_ID_COL
                case EquipmentSlot.LEGS:
                    column = self.USER_EQUIPMENT_LEGGEAR_ID_COL
                case EquipmentSlot.ACCESSORY:
                    column = self.USER_EQUIPMENT_ACCESSORY_1_ID_COL

        command = f"""
            UPDATE {self.USER_EQUIPMENT_TABLE} SET
            {column}
            = ?
            WHERE {self.USER_EQUIPMENT_GUILD_ID_COL} = ?
            AND {self.USER_EQUIPMENT_MEMBER_ID_COL} = ?;
        """

        id = None
        if gear is not None:
            id = gear.id
            # await self.update_lock_gear_by_id(id, lock=True)

        task = (id, guild_id, member_id)
        await self.__query_insert(command, task)

    async def get_scrappable_equipment_by_user(
        self, guild_id: int, member_id: int, type: Base = Base.GEAR
    ) -> list[Gear]:

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            WHERE {self.USER_GEAR_GUILD_ID_COL} = ?
            AND {self.USER_GEAR_MEMBER_ID_COL} = ?
            AND {self.USER_GEAR_BASE_TYPE_COL} = ?
            AND {self.USER_GEAR_IS_SCRAPPED_COL} = 0
            AND {self.USER_GEAR_IS_LOCKED_COL} = 0
            ;
        """
        task = (guild_id, member_id, type.value)
        rows = await self.__query_select(command, task)
        if not rows:
            return []

        equipped_gear = await self.get_user_equipment(guild_id, member_id)
        equipped_ids = [gear.id for gear in equipped_gear.gear]

        equipment = []
        for row in rows:
            id = row[self.USER_GEAR_ID_COL]
            if id in equipped_ids:
                continue
            match type:
                case Base.GEAR:
                    item = await self.get_gear_by_id(id)
                case Base.SKILL:
                    item = await self.get_skill_by_id(id)
            equipment.append(item)

        return equipment

    async def get_user_enchantment_inventory(
        self, guild_id: int, member_id: int
    ) -> list[Enchantment]:

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            WHERE {self.USER_GEAR_GUILD_ID_COL} = ?
            AND {self.USER_GEAR_MEMBER_ID_COL} = ?
            AND {self.USER_GEAR_BASE_TYPE_COL} = ?
            AND {self.USER_GEAR_IS_SCRAPPED_COL} = 0
            ;
        """
        task = (guild_id, member_id, Base.ENCHANTMENT)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        enchantments = []
        for row in rows:
            enchantment = await self.get_enchantment_by_id(row[self.USER_GEAR_ID_COL])
            enchantments.append(enchantment)

        return enchantments

    async def get_user_skill_inventory(
        self, guild_id: int, member_id: int
    ) -> list[Skill]:

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            LEFT JOIN {self.USER_EQUIPPED_SKILLS_TABLE} ON {self.USER_EQUIPPED_SKILLS_SKILL_ID_COL} = {self.USER_GEAR_ID_COL}
            WHERE {self.USER_GEAR_GUILD_ID_COL} = ?
            AND {self.USER_GEAR_MEMBER_ID_COL} = ?
            AND {self.USER_GEAR_BASE_TYPE_COL} = ?
            AND {self.USER_GEAR_IS_SCRAPPED_COL} = 0
            ;
        """
        task = (guild_id, member_id, Base.SKILL)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        skills = []
        for row in rows:
            if row[self.USER_EQUIPPED_SKILLS_SKILL_ID_COL] is not None:
                continue
            gear_piece = await self.get_skill_by_id(row[self.USER_GEAR_ID_COL])
            skills.append(gear_piece)

        return skills

    async def get_user_armory(self, guild_id: int, member_id: int) -> list[Gear]:

        command = f""" 
            SELECT * FROM {self.USER_GEAR_TABLE} 
            WHERE {self.USER_GEAR_GUILD_ID_COL} = ?
            AND {self.USER_GEAR_MEMBER_ID_COL} = ?
            AND {self.USER_GEAR_BASE_TYPE_COL} = ?
            AND {self.USER_GEAR_IS_SCRAPPED_COL} = 0
            ;
        """
        task = (guild_id, member_id, Base.GEAR)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        armory = []
        for row in rows:
            gear_piece = await self.get_gear_by_id(row[self.USER_GEAR_ID_COL])
            armory.append(gear_piece)

        return armory

    async def get_user_enchantment_stacks_used(
        self, guild_id: int, member_id: int
    ) -> dict[int, int]:
        command = f"""
            SELECT * FROM {self.COMBAT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.COMBAT_EVENT_TABLE}.{self.COMBAT_EVENT_ID_COL}
            LEFT JOIN {self.USER_GEAR_TABLE} ON {self.COMBAT_EVENT_SKILL_ID} = {self.USER_GEAR_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.COMBAT_EVENT_MEMBER_ID} = ?
            AND {self.COMBAT_EVENT_TYPE_COL} = ?
            ORDER BY {self.EVENT_ID_COL} DESC;
        """
        task = (guild_id, member_id, CombatEventType.ENCHANTMENT_EFFECT)
        rows = await self.__query_select(command, task)
        if not rows:
            return {}

        active_encounters = await self.get_encounter_participants(guild_id)

        current_encounter_id = None

        for encounter_id, members in active_encounters.items():
            if member_id in members:
                current_encounter_id = encounter_id
                break

        stacks_used = {}
        for row in rows:
            if (
                row[self.COMBAT_EVENT_SKILL_TYPE] is None
                or row[self.COMBAT_EVENT_SKILL_TYPE] not in EnchantmentType
            ):
                continue

            enchantment_type = EnchantmentType(row[self.COMBAT_EVENT_SKILL_TYPE])

            enchantment_id = row[self.COMBAT_EVENT_SKILL_ID]
            if enchantment_id is None:
                continue

            base_class = globals()[enchantment_type]
            base_enchantment: BaseEnchantment = base_class()  # noqa: F405

            if base_enchantment.reset_after_encounter:
                if current_encounter_id is None:
                    continue

                encounter_id = row[self.COMBAT_EVENT_ENCOUNTER_ID_COL]
                if current_encounter_id != encounter_id:
                    continue

            if enchantment_id not in stacks_used:
                stacks_used[enchantment_id] = 1
            else:
                stacks_used[enchantment_id] += 1

        return stacks_used

    async def get_user_skill_stacks_used(
        self, guild_id: int, member_id: int
    ) -> dict[int, int]:
        command = f"""
            SELECT * FROM {self.COMBAT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.COMBAT_EVENT_TABLE}.{self.COMBAT_EVENT_ID_COL}
            LEFT JOIN {self.USER_GEAR_TABLE} ON {self.COMBAT_EVENT_SKILL_ID} = {self.USER_GEAR_ID_COL}
            LEFT JOIN {self.USER_EQUIPPED_SKILLS_TABLE} ON {self.COMBAT_EVENT_SKILL_ID} = {self.USER_EQUIPPED_SKILLS_SKILL_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.COMBAT_EVENT_MEMBER_ID} = ?
            AND {self.COMBAT_EVENT_TYPE_COL} = ?
            ORDER BY {self.EVENT_ID_COL} DESC;
        """
        task = (guild_id, member_id, CombatEventType.MEMBER_TURN)
        rows = await self.__query_select(command, task)
        if not rows:
            return {}

        active_encounters = await self.get_encounter_participants(guild_id)

        current_encounter_id = None

        for encounter_id, members in active_encounters.items():
            if member_id in members:
                current_encounter_id = encounter_id
                break

        stacks_used = {}
        for row in rows:
            if (
                row[self.COMBAT_EVENT_SKILL_TYPE] is None
                or row[self.COMBAT_EVENT_SKILL_TYPE] not in SkillType
            ):
                continue

            skill_type = SkillType(row[self.COMBAT_EVENT_SKILL_TYPE])

            skill_id = row[self.COMBAT_EVENT_SKILL_ID]
            if skill_id is None:
                continue

            base_class = globals()[skill_type]
            base_skill: BaseSkill = base_class()  # noqa: F405

            if base_skill.reset_after_encounter:
                if current_encounter_id is None:
                    continue

                encounter_id = row[self.COMBAT_EVENT_ENCOUNTER_ID_COL]
                if current_encounter_id != encounter_id:
                    continue

            if skill_id not in stacks_used:
                stacks_used[skill_id] = 1
            else:
                stacks_used[skill_id] += 1

        return stacks_used

    async def get_opponent_skill_stacks_used(
        self, encounter_id: int | None
    ) -> dict[SkillType, int]:
        if encounter_id is None:
            return {}

        command = f"""
            SELECT * FROM {self.COMBAT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.COMBAT_EVENT_TABLE}.{self.COMBAT_EVENT_ID_COL}
            WHERE {self.COMBAT_EVENT_ENCOUNTER_ID_COL} = {int(encounter_id)}
            ORDER BY {self.EVENT_ID_COL} DESC;
        """
        rows = await self.__query_select(command)
        if not rows:
            return {}

        stacks_used = {}
        for row in rows:
            event_type = row[self.COMBAT_EVENT_TYPE_COL]
            if event_type in [
                CombatEventType.ENEMY_END_TURN,
                CombatEventType.MEMBER_END_TURN,
            ]:
                continue

            with contextlib.suppress(Exception):
                skill_type = SkillType(row[self.COMBAT_EVENT_SKILL_TYPE])

                if skill_type not in stacks_used:
                    stacks_used[skill_type] = 1
                else:
                    stacks_used[skill_type] += 1

        return stacks_used

    async def clear_selected_user_skills(
        self,
        guild_id: int,
        member_id: int,
        skill_id: int = None,
    ):
        command = f""" 
            DELETE FROM {self.USER_EQUIPPED_SKILLS_TABLE} 
            WHERE {self.USER_EQUIPPED_SKILLS_GUILD_ID_COL} = ?
            AND {self.USER_EQUIPPED_SKILLS_MEMBER_ID_COL} = ?
        """

        if skill_id is not None:
            command += f"""
                AND {self.USER_EQUIPPED_SKILLS_SKILL_ID_COL} = {int(skill_id)}
            """

        command += ";"

        task = (guild_id, member_id)
        return await self.__query_insert(command, task)

    async def set_selected_user_skills(
        self, guild_id: int, member_id: int, skills: dict[int, Skill]
    ):
        await self.clear_selected_user_skills(guild_id, member_id)

        skill_ids = [skill.id for skill in skills.values() if skill is not None]
        await self.delete_gear_by_ids(skill_ids)

        for slot, skill in skills.items():
            if skill is None:
                continue
            command = f"""
                INSERT INTO {self.USER_EQUIPPED_SKILLS_TABLE} (
                {self.USER_EQUIPPED_SKILLS_GUILD_ID_COL}, 
                {self.USER_EQUIPPED_SKILLS_MEMBER_ID_COL}, 
                {self.USER_EQUIPPED_SKILLS_SKILL_ID_COL}, 
                {self.USER_EQUIPPED_SKILLS_SKILL_TYPE_COL}, 
                {self.USER_EQUIPPED_SKILLS_SLOT_COL}) 
                VALUES (?, ?, ?, ?, ?);
            """
            task = (guild_id, member_id, skill.id, skill.type, slot)
            await self.__query_insert(command, task)

    async def get_karma_events_by_giver_id(
        self,
        giver_id: int,
        guild_id: int,
        positive: bool = None,
    ) -> list[KarmaEvent]:

        if positive is None:
            amount = ""
        elif positive:
            amount = f"AND {self.KARMA_EVENT_AMOUNT} >= 0"
        else:
            amount = f"AND {self.KARMA_EVENT_AMOUNT} < 0"

        command = f"""
            SELECT * FROM {self.KARMA_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.KARMA_EVENT_TABLE}.{self.KARMA_EVENT_ID_COL}
            WHERE {self.KARMA_EVENT_GIVER_ID} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            {amount}
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC;
        """
        task = (giver_id, guild_id)

        rows = await self.__query_select(command, task)
        if not rows:
            return []

        return [KarmaEvent.from_db_row(row) for row in rows]

    async def get_karma_events_by_recipient_id(
        self,
        recipient_id: int,
        guild_id: int,
    ) -> list[KarmaEvent]:
        command = f"""
            SELECT * FROM {self.KARMA_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.KARMA_EVENT_TABLE}.{self.KARMA_EVENT_ID_COL}
            WHERE {self.KARMA_EVENT_RECIPIENT_ID} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC;
        """
        task = (recipient_id, guild_id)

        rows = await self.__query_select(command, task)
        if not rows:
            return []

        return [KarmaEvent.from_db_row(row) for row in rows]

    async def get_karma_events_by_guild(
        self, guild_id: int, season: int = None, positive: bool = None
    ) -> list[KarmaEvent]:
        start_timestamp, end_timestamp = await self.__get_season_interval(
            guild_id, season
        )

        if positive is None:
            amount = ""
        elif positive:
            amount = f"AND {self.KARMA_EVENT_AMOUNT} >= 0"
        else:
            amount = f"AND {self.KARMA_EVENT_AMOUNT} < 0"

        command = f"""
            SELECT * FROM {self.KARMA_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.KARMA_EVENT_TABLE}.{self.KARMA_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = ?
            AND {self.EVENT_TIMESTAMP_COL} > ?
            {amount}
            AND {self.EVENT_TIMESTAMP_COL} <= ?;
        """
        task = (guild_id, start_timestamp, end_timestamp)
        rows = await self.__query_select(command, task)
        if not rows:
            return []
        return [KarmaEvent.from_db_row(row) for row in rows]

    async def get_status_effects_by_encounter(
        self,
        encounter_id: int,
    ) -> dict[int, list[StatusEffectEvent]]:
        command = f"""
            SELECT * FROM {self.STATUS_EFFECT_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.STATUS_EFFECT_EVENT_TABLE}.{self.STATUS_EFFECT_EVENT_ID_COL}
            WHERE {self.STATUS_EFFECT_EVENT_ENCOUNTER_ID_COL} = {int(encounter_id)}
            ;
        """

        rows = await self.__query_select(command)

        if not rows or len(rows) < 1:
            return {}

        transformed = {}
        for row in rows:
            user_id = row[self.STATUS_EFFECT_EVENT_ACTOR_ID_COL]
            event = StatusEffectEvent.from_db_row(row)
            if user_id not in transformed:
                transformed[user_id] = [event]
            else:
                transformed[user_id].append(event)

        return transformed

    async def get_already_bought_daily_gear(
        self,
        member_id: int,
        guild_id: int,
    ) -> list[int]:
        command = f"""
            SELECT * FROM {self.EQUIPMENT_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.EQUIPMENT_EVENT_TABLE}.{self.EQUIPMENT_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.EQUIPMENT_EVENT_MEMBER_ID} = ?
            AND {self.EQUIPMENT_EVENT_EQUIPMENT_EVENT_TYPE} = ?
            ;
        """

        task = (guild_id, member_id, EquipmentEventType.SHOP_BUY.value)
        rows = await self.__query_select(command, task)

        if not rows or len(rows) < 1:
            return {}

        item_ids = []
        for row in rows:
            item_ids.append(int(row[self.EQUIPMENT_EVENT_ITEM_ID]))

        return item_ids

    async def set_user_setting(
        self, member_id: int, guild_id: int, setting_id: str, value
    ):
        command = f"""
            INSERT INTO {self.USER_SETTINGS_TABLE} (
            {self.USER_SETTINGS_GUILD_ID_COL},
            {self.USER_SETTINGS_MEMBER_ID_COL},
            {self.USER_SETTINGS_SETTING_ID_COL},
            {self.USER_SETTINGS_VALUE_COL})
            VALUES (?, ?, ?, ?)
            ON CONFLICT(
            {self.USER_SETTINGS_GUILD_ID_COL},
            {self.USER_SETTINGS_MEMBER_ID_COL},
            {self.USER_SETTINGS_SETTING_ID_COL}
            ) 
            DO UPDATE SET 
            {self.USER_SETTINGS_VALUE_COL}=excluded.{self.USER_SETTINGS_VALUE_COL};
        """
        task = (guild_id, member_id, setting_id, value)

        return await self.__query_insert(command, task)

    async def get_user_setting(
        self,
        member_id: int,
        guild_id: int,
        setting_id: str,
    ):
        command = f"""
            SELECT * FROM {self.USER_SETTINGS_TABLE} 
            WHERE {self.USER_SETTINGS_GUILD_ID_COL} = ?
            AND {self.USER_SETTINGS_MEMBER_ID_COL} = ?
            AND {self.USER_SETTINGS_SETTING_ID_COL} = ?
            LIMIT 1;
        """

        task = (guild_id, member_id, setting_id)
        rows = await self.__query_select(command, task)

        if not rows or len(rows) < 1:
            return None

        return rows[0][self.USER_SETTINGS_VALUE_COL]

    async def get_guild_current_season_number(
        self,
        guild_id: int,
    ) -> int:
        command = f"""
            SELECT * FROM {self.GUILD_SEASON_TABLE} 
            WHERE {self.GUILD_SEASON_GUILD_ID_COL} = {int(guild_id)}
            ORDER BY {self.GUILD_SEASON_SEASON_NR_COL} DESC
            LIMIT 1;
        """

        rows = await self.__query_select(command)

        if not rows or len(rows) < 1:
            return 1

        return rows[0][self.GUILD_SEASON_SEASON_NR_COL] + 1

    async def get_guild_current_season_start(
        self,
        guild_id: int,
    ) -> int:
        command = f"""
            SELECT * FROM {self.GUILD_SEASON_TABLE} 
            WHERE {self.GUILD_SEASON_GUILD_ID_COL} = {int(guild_id)}
            ORDER BY {self.GUILD_SEASON_SEASON_NR_COL} DESC
            LIMIT 1;
        """

        rows = await self.__query_select(command)

        if not rows or len(rows) < 1:
            return 0

        return rows[0][self.GUILD_SEASON_END_TIMESTAMP_COL]

    async def get_guild_season_end(
        self,
        guild_id: int,
        season_nr: int,
    ) -> int:
        command = f"""
            SELECT * FROM {self.GUILD_SEASON_TABLE} 
            WHERE {self.GUILD_SEASON_GUILD_ID_COL} = ?
            AND {self.GUILD_SEASON_SEASON_NR_COL} = ?
            LIMIT 1;
        """

        task = (guild_id, season_nr)
        rows = await self.__query_select(command, task)

        if not rows or len(rows) < 1:
            return 0

        return rows[0][self.GUILD_SEASON_END_TIMESTAMP_COL]

    async def end_current_season(
        self,
        guild_id: int,
    ) -> datetime.datetime:
        current_season = await self.get_guild_current_season_number(guild_id)
        command = f"""
            INSERT INTO {self.GUILD_SEASON_TABLE} (
            {self.GUILD_SEASON_GUILD_ID_COL},
            {self.GUILD_SEASON_SEASON_NR_COL},
            {self.GUILD_SEASON_END_TIMESTAMP_COL})
            VALUES (?, ?, ?)
            ON CONFLICT(
            {self.GUILD_SEASON_GUILD_ID_COL},
            {self.GUILD_SEASON_SEASON_NR_COL}
            ) 
            DO UPDATE SET 
            {self.GUILD_SEASON_END_TIMESTAMP_COL}=excluded.{self.GUILD_SEASON_END_TIMESTAMP_COL};
        """
        timestamp = datetime.datetime.now().timestamp()
        task = (guild_id, current_season, timestamp)

        return await self.__query_insert(command, task)
