import json
import sqlite3
import traceback
import discord

from typing import Dict, List, Tuple
from sqlite3 import Error
from discord.ext import commands
from BotLogger import BotLogger
from datalayer.LootBox import LootBox
from datalayer.UserInventory import UserInventory
from datalayer.UserJail import UserJail
from datalayer.Quote import Quote
from events.BeansEvent import BeansEvent
from events.BeansEventType import BeansEventType
from events.BotEvent import BotEvent
from events.EventType import EventType
from events.InteractionEvent import InteractionEvent
from events.InventoryEvent import InventoryEvent
from events.JailEvent import JailEvent
from events.LootBoxEvent import LootBoxEvent
from events.LootBoxEventType import LootBoxEventType
from events.QuoteEvent import QuoteEvent
from events.SpamEvent import SpamEvent
from events.TimeoutEvent import TimeoutEvent
from shop.ItemType import ItemType
from view.EmojiType import EmojiType

class Database():    
    
    SETTINGS_TABLE = 'guildsettings'
    SETTINGS_GUILD_ID_COL = 'gset_guild_id'
    SETTINGS_MODULE_COL = 'gset_module'
    SETTINGS_KEY_COL = 'gset_key'
    SETTINGS_VALUE_COL = 'gset_value'
    CREATE_SETTINGS_TABLE = f'''
    CREATE TABLE if not exists {SETTINGS_TABLE} (
        {SETTINGS_GUILD_ID_COL} INTEGER, 
        {SETTINGS_MODULE_COL} TEXT, 
        {SETTINGS_KEY_COL} TEXT, 
        {SETTINGS_VALUE_COL}, 
        PRIMARY KEY ({SETTINGS_GUILD_ID_COL}, {SETTINGS_MODULE_COL}, {SETTINGS_KEY_COL})
    );'''
    
    TIMEOUT_TRACKER_TABLE = 'timeout_tracking'
    TIMEOUT_TRACKER_GUILD_ID_COL = 'titr_guild_id'
    TIMEOUT_TRACKER_MEMBER_COL = 'titr_member'
    TIMEOUT_TRACKER_COUNT_COL = 'titr_count'
    CREATE_TIMEOUT_TRACKER_TABLE = f'''
    CREATE TABLE if not exists {TIMEOUT_TRACKER_TABLE} (
        {TIMEOUT_TRACKER_GUILD_ID_COL} INTEGER,
        {TIMEOUT_TRACKER_MEMBER_COL} INTEGER, 
        {TIMEOUT_TRACKER_COUNT_COL} INTEGER,
        PRIMARY KEY ({TIMEOUT_TRACKER_GUILD_ID_COL}, {TIMEOUT_TRACKER_MEMBER_COL})
    );'''
    
    JAIL_TABLE = 'jail'
    JAIL_ID_COL = 'jail_id'
    JAIL_GUILD_ID_COL = 'jail_guild_id'
    JAIL_MEMBER_COL = 'jail_member'
    JAIL_JAILED_ON_COL = 'jail_jailed_on'
    JAIL_RELEASED_ON_COL = 'jail_released_on'
    CREATE_JAIL_TABLE = f'''
    CREATE TABLE if not exists {JAIL_TABLE} (
        {JAIL_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {JAIL_GUILD_ID_COL} INTEGER, 
        {JAIL_MEMBER_COL} INTEGER, 
        {JAIL_JAILED_ON_COL} INTEGER, 
        {JAIL_RELEASED_ON_COL} INTEGER
    );'''
    
    EVENT_TABLE = 'events'
    EVENT_ID_COL = 'evnt_id'
    EVENT_TIMESTAMP_COL = 'evnt_timestamp'
    EVENT_GUILD_ID_COL = 'evnt_guild_id'
    EVENT_TYPE_COL = 'evnt_type'
    CREATE_EVENT_TABLE = f'''
    CREATE TABLE if not exists {EVENT_TABLE} (
        {EVENT_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT, 
        {EVENT_TIMESTAMP_COL} INTEGER,
        {EVENT_GUILD_ID_COL} INTEGER,
        {EVENT_TYPE_COL} TEXT
    );'''
    
    INTERACTION_EVENT_TABLE = 'interactionevents'
    INTERACTION_EVENT_ID_COL = 'inev_id'
    INTERACTION_EVENT_TYPE_COL= 'inev_type'
    INTERACTION_EVENT_FROM_COL = 'inev_from_member'
    INTERACTION_EVENT_TO_COL = 'inev_to_member'
    CREATE_INTERACTION_EVENT_TABLE = f'''
    CREATE TABLE if not exists {INTERACTION_EVENT_TABLE} (
        {INTERACTION_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {INTERACTION_EVENT_TYPE_COL} TEXT, 
        {INTERACTION_EVENT_FROM_COL} INTEGER, 
        {INTERACTION_EVENT_TO_COL} INTEGER,
        PRIMARY KEY ({INTERACTION_EVENT_ID_COL})
    );'''
    
    JAIL_EVENT_TABLE = 'jailevents'
    JAIL_EVENT_ID_COL = 'jaev_id'
    JAIL_EVENT_TYPE_COL = 'jaev_type'
    JAIL_EVENT_BY_COL = 'jaev_by'
    JAIL_EVENT_DURATION_COL = 'jaev_duration'
    JAIL_EVENT_JAILREFERENCE_COL = 'jaev_sentence_id'
    CREATE_JAIL_EVENT_TABLE = f'''
    CREATE TABLE if not exists {JAIL_EVENT_TABLE} (
        {JAIL_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {JAIL_EVENT_TYPE_COL} TEXT, 
        {JAIL_EVENT_BY_COL} INTEGER, 
        {JAIL_EVENT_DURATION_COL} INTEGER, 
        {JAIL_EVENT_JAILREFERENCE_COL} INTEGER REFERENCES {JAIL_TABLE} ({JAIL_ID_COL}),
        PRIMARY KEY ({JAIL_EVENT_ID_COL})
    );'''
    
    TIMEOUT_EVENT_TABLE = 'timeoutevents'
    TIMEOUT_EVENT_ID_COL = 'toev_id'
    TIMEOUT_EVENT_MEMBER_COL = 'toev_member'
    TIMEOUT_EVENT_DURATION_COL = 'toev_duration'
    CREATE_TIMEOUT_EVENT_TABLE = f'''
    CREATE TABLE if not exists {TIMEOUT_EVENT_TABLE} (
        {TIMEOUT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {TIMEOUT_EVENT_MEMBER_COL} INTEGER, 
        {TIMEOUT_EVENT_DURATION_COL} INTEGER,
        PRIMARY KEY ({TIMEOUT_EVENT_ID_COL})
    );'''
    
    SPAM_EVENT_TABLE = 'spamevents'
    SPAM_EVENT_ID_COL = 'spev_id'
    SPAM_EVENT_MEMBER_COL = 'spev_member'
    CREATE_SPAM_EVENT_TABLE = f'''
    CREATE TABLE if not exists {SPAM_EVENT_TABLE} (
        {SPAM_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {SPAM_EVENT_MEMBER_COL} INTEGER, 
        PRIMARY KEY ({SPAM_EVENT_ID_COL})
    );'''
    
    QUOTE_TABLE = 'quotes'
    QUOTE_ID_COL = 'quot_id'
    QUOTE_GUILD_COL = 'quot_guild_id'
    QUOTE_MEMBER_COL = 'quot_member_id'
    QUOTE_MEMBER_NAME_COL = 'quot_member_name'
    QUOTE_SAVED_BY_COL = 'quot_saved_by'
    QUOTE_MESSAGE_COL = 'quot_message_id'
    QUOTE_CHANNEL_COL = 'quot_channel_id'
    QUOTE_TIMESTAMP_COL = 'quot_timestamp'
    QUOTE_TEXT_COL = 'quot_message_content'
    CREATE_QUOTE_TABLE = f'''
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
    );'''
    
    QUOTE_EVENT_TABLE = 'quoteevents'
    QUOTE_EVENT_ID_COL = 'quev_id'
    QUOTE_EVENT_REF_COL = 'quev_quote_id'
    CREATE_QUOTE_EVENT_TABLE = f'''
    CREATE TABLE if not exists {QUOTE_EVENT_TABLE} (
        {QUOTE_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {QUOTE_EVENT_REF_COL} INTEGER REFERENCES {QUOTE_TABLE} ({QUOTE_ID_COL}),
        PRIMARY KEY ({QUOTE_EVENT_ID_COL})
    );'''
    
    BEANS_EVENT_TABLE = 'beansevents'
    BEANS_EVENT_ID_COL = 'bnev_id'
    BEANS_EVENT_MEMBER_COL = 'bnev_member'
    BEANS_EVENT_TYPE_COL = 'bnev_type'
    BEANS_EVENT_VALUE_COL = 'bnev_value'
    CREATE_BEANS_EVENT_TABLE = f'''
    CREATE TABLE if not exists {BEANS_EVENT_TABLE} (
        {BEANS_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {BEANS_EVENT_MEMBER_COL} INTEGER, 
        {BEANS_EVENT_TYPE_COL} TEXT,
        {BEANS_EVENT_VALUE_COL} INTEGER,
        PRIMARY KEY ({BEANS_EVENT_ID_COL})
    );'''
    
    INVENTORY_EVENT_TABLE = 'inventoryevents'
    INVENTORY_EVENT_ID_COL = 'inve_id'
    INVENTORY_EVENT_MEMBER_COL = 'inve_member_id'
    INVENTORY_EVENT_ITEM_TYPE_COL = 'inve_item_type'
    INVENTORY_EVENT_BEANS_EVENT_COL = 'inve_beans_event_id'
    INVENTORY_EVENT_AMOUNT_COL = 'inve_amount'
    CREATE_INVENTORY_EVENT_TABLE = f'''
    CREATE TABLE if not exists {INVENTORY_EVENT_TABLE} (
        {INVENTORY_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {INVENTORY_EVENT_MEMBER_COL} INTEGER, 
        {INVENTORY_EVENT_ITEM_TYPE_COL} TEXT, 
        {INVENTORY_EVENT_BEANS_EVENT_COL} INTEGER REFERENCES {BEANS_EVENT_TABLE} ({BEANS_EVENT_ID_COL}),
        {INVENTORY_EVENT_AMOUNT_COL} INTEGER,
        PRIMARY KEY ({INVENTORY_EVENT_ID_COL})
    );'''
    
    LOOTBOX_TABLE = 'lootbox'
    LOOTBOX_ID_COL = 'lobo_id'
    LOOTBOX_GUILD_COL = 'lobo_guild_id'
    LOOTBOX_MESSAGE_ID_COL = 'lobo_message_id_id'
    LOOTBOX_ITEM_TYPE_COL = 'lobo_item_type'
    LOOTBOX_BEANS_COL = 'lobo_beans'
    CREATE_LOOTBOX_TABLE = f'''
    CREATE TABLE if not exists {LOOTBOX_TABLE} (
        {LOOTBOX_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {LOOTBOX_GUILD_COL} INTEGER, 
        {LOOTBOX_MESSAGE_ID_COL} INTEGER, 
        {LOOTBOX_ITEM_TYPE_COL} TEXT, 
        {LOOTBOX_BEANS_COL} INTEGER
    );'''
    
    LOOTBOX_EVENT_TABLE = 'lootboxevents'
    LOOTBOX_EVENT_ID_COL = 'lbev_event_id'
    LOOTBOX_EVENT_LOOTBOX_ID_COL = 'lbev_lootbox_id'
    LOOTBOX_EVENT_MEMBER_COL = 'lbev_member_id'
    LOOTBOX_EVENT_TYPE_COL = 'lbev_event_type'
    CREATE_LOOTBOX_EVENT_TABLE = f'''
    CREATE TABLE if not exists {LOOTBOX_EVENT_TABLE} (
        {LOOTBOX_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {LOOTBOX_EVENT_LOOTBOX_ID_COL} INTEGER REFERENCES {LOOTBOX_TABLE} ({LOOTBOX_ID_COL}),
        {LOOTBOX_EVENT_MEMBER_COL} INTEGER, 
        {LOOTBOX_EVENT_TYPE_COL} TEXT,
        PRIMARY KEY ({LOOTBOX_EVENT_ID_COL})
    );'''
    
    
    CUSTOM_COLOR_TABLE = 'customcolor'
    CUSTOM_COLOR_GUILD_COL = 'cuco_guild_id'
    CUSTOM_COLOR_MEMBER_COL = 'cuco_member_id'
    CUSTOM_COLOR_ROLE_COL = 'cuco_role_id'
    CUSTOM_COLOR_COLOR_COL = 'cuco_color'
    CREATE_CUSTOM_COLOR_TABLE = f'''
    CREATE TABLE if not exists {CUSTOM_COLOR_TABLE} (
        {CUSTOM_COLOR_GUILD_COL} INTEGER, 
        {CUSTOM_COLOR_MEMBER_COL}  INTEGER,
        {CUSTOM_COLOR_ROLE_COL} INTEGER, 
        {CUSTOM_COLOR_COLOR_COL} TEXT,
        PRIMARY KEY ({CUSTOM_COLOR_MEMBER_COL}, {CUSTOM_COLOR_GUILD_COL})
    );'''
    
    BULLY_REACT_TABLE = 'bullyreact'
    BULLY_REACT_GUILD_COL = 'buli_guild_id'
    BULLY_REACT_MEMBER_COL = 'buli_member_id'
    BULLY_REACT_TARGET_COL = 'buli_target_id'
    BULLY_REACT_EMOJI_TYPE_COL = 'buli_type'
    BULLY_REACT_EMOJI_VALUE_COL = 'buli_value'
    CREATE_BULLY_REACT_TABLE = f'''
    CREATE TABLE if not exists {BULLY_REACT_TABLE} (
        {BULLY_REACT_GUILD_COL} INTEGER, 
        {BULLY_REACT_MEMBER_COL}  INTEGER,
        {BULLY_REACT_TARGET_COL} INTEGER, 
        {BULLY_REACT_EMOJI_TYPE_COL} TEXT,
        {BULLY_REACT_EMOJI_VALUE_COL} TEXT,
        PRIMARY KEY ({BULLY_REACT_GUILD_COL}, {BULLY_REACT_MEMBER_COL})
    );'''
    
    def __init__(self, bot: commands.Bot, logger: BotLogger, db_file: str):
        
        self.conn = None
        self.bot = bot
        self.logger = logger
        
        try:
            self.conn = sqlite3.connect(db_file)
            self.logger.log("DB",f'Loaded DB version {sqlite3.version} from {db_file}.')
            
            c = self.conn.cursor()
            
            c.execute(self.CREATE_SETTINGS_TABLE)
            c.execute(self.CREATE_JAIL_TABLE)
            c.execute(self.CREATE_EVENT_TABLE)
            c.execute(self.CREATE_QUOTE_TABLE)
            c.execute(self.CREATE_TIMEOUT_TRACKER_TABLE)
            c.execute(self.CREATE_INTERACTION_EVENT_TABLE)
            c.execute(self.CREATE_JAIL_EVENT_TABLE)
            c.execute(self.CREATE_TIMEOUT_EVENT_TABLE)
            c.execute(self.CREATE_SPAM_EVENT_TABLE)
            c.execute(self.CREATE_QUOTE_EVENT_TABLE)
            c.execute(self.CREATE_BEANS_EVENT_TABLE)
            c.execute(self.CREATE_INVENTORY_EVENT_TABLE)
            c.execute(self.CREATE_LOOTBOX_TABLE)
            c.execute(self.CREATE_LOOTBOX_EVENT_TABLE)
            c.execute(self.CREATE_CUSTOM_COLOR_TABLE)
            c.execute(self.CREATE_BULLY_REACT_TABLE)
            c.close()
            
        except Error as e:
            traceback.print_stack()
            traceback.print_exc()
            self.logger.error("DB",e)

    def __query_select(self, query: str, task = None):
        try:
            c = self.conn.cursor()
            c.execute(query, task) if task is not None else c.execute(query)
            rows = c.fetchall()
            headings = [x[0] for x in c.description]
            
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_stack()
            traceback.print_exc()
            return None 
    
    def __query_insert(self, query: str, task = None) -> int:
        try:
            cur = self.conn.cursor()
            cur.execute(query, task) if task is not None else cur.execute(query)
            insert_id = cur.lastrowid
            self.conn.commit()
            
            return insert_id
        
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_stack()
            traceback.print_exc()    
            return None
    
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
                
    def get_setting(self, guild_id: int, module: str, key: str):
        command = f'''
            SELECT * FROM {self.SETTINGS_TABLE} 
            WHERE {self.SETTINGS_GUILD_ID_COL}=? AND {self.SETTINGS_MODULE_COL}=? AND {self.SETTINGS_KEY_COL}=? 
            LIMIT 1;
        '''
        task = (int(guild_id), str(module), str(key))
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        
        return json.loads(rows[0][self.SETTINGS_VALUE_COL])
    
    def update_setting(self, guild_id: int, module: str, key: str, value):
        try:
            value = json.dumps(value)
            
            command = f'''
                INSERT INTO {self.SETTINGS_TABLE} ({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}, {self.SETTINGS_VALUE_COL}) 
                VALUES (?, ?, ?, ?) 
                ON CONFLICT({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}) 
                DO UPDATE SET {self.SETTINGS_VALUE_COL}=excluded.{self.SETTINGS_VALUE_COL};
            '''
            task = (int(guild_id), str(module), str(key), value)
        
            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_stack()
            traceback.print_exc()
    
    def __create_base_event(self, event: BotEvent) -> int:
        command = f'''
                INSERT INTO {self.EVENT_TABLE} (
                {self.EVENT_TIMESTAMP_COL}, 
                {self.EVENT_GUILD_ID_COL}, 
                {self.EVENT_TYPE_COL}) 
                VALUES (?, ?, ?);
            '''
        task = (event.get_timestamp(), event.get_guild_id(), event.get_type())
        
        return self.__query_insert(command, task)
    
    def __create_interaction_event(self, event_id: int, event: InteractionEvent) -> int:
        command = f'''
            INSERT INTO {self.INTERACTION_EVENT_TABLE} (
            {self.INTERACTION_EVENT_ID_COL},
            {self.INTERACTION_EVENT_TYPE_COL},
            {self.INTERACTION_EVENT_FROM_COL},
            {self.INTERACTION_EVENT_TO_COL}) 
            VALUES (?, ?, ?, ?);
        '''
        task = (event_id, event.get_interaction_type(), event.get_from_user(), event.get_to_user())

        return self.__query_insert(command, task)

    def __create_timeout_event(self, event_id: int, event: TimeoutEvent) -> int:
        command = f'''
            INSERT INTO {self.TIMEOUT_EVENT_TABLE} (
            {self.TIMEOUT_EVENT_ID_COL},
            {self.TIMEOUT_EVENT_MEMBER_COL},
            {self.TIMEOUT_EVENT_DURATION_COL})
            VALUES (?, ?, ?);
        '''
        task = (event_id, event.get_member(), event.get_duration())

        return self.__query_insert(command, task)
    
    def __create_spam_event(self, event_id: int, event: SpamEvent) -> int:
        command = f'''
            INSERT INTO {self.SPAM_EVENT_TABLE} (
            {self.SPAM_EVENT_ID_COL},
            {self.SPAM_EVENT_MEMBER_COL})
            VALUES (?, ?);
        '''
        task = (event_id, event.get_member())

        return self.__query_insert(command, task)
    
    def __create_jail_event(self, event_id: int, event: JailEvent) -> int:
        command = f'''
            INSERT INTO {self.JAIL_EVENT_TABLE} (
            {self.JAIL_EVENT_ID_COL},
            {self.JAIL_EVENT_TYPE_COL},
            {self.JAIL_EVENT_BY_COL},
            {self.JAIL_EVENT_DURATION_COL},
            {self.JAIL_EVENT_JAILREFERENCE_COL})
            VALUES (?, ?, ?, ?, ?);
        '''
        task = (event_id, event.get_jail_event_type(), event.get_caused_by(), event.get_duration(), event.get_jail_id())

        return self.__query_insert(command, task)
    
    def __create_quote_event(self, event_id: int, event: QuoteEvent) -> int:
        command = f'''
            INSERT INTO {self.QUOTE_EVENT_TABLE} (
            {self.QUOTE_EVENT_ID_COL},
            {self.QUOTE_EVENT_REF_COL})
            VALUES (?, ?);
        '''
        task = (event_id, event.get_quote_id())
        
        return self.__query_insert(command, task)
    
    def __create_beans_event(self, event_id: int, event: BeansEvent) -> int:
        command = f'''
            INSERT INTO {self.BEANS_EVENT_TABLE} (
            {self.BEANS_EVENT_ID_COL},
            {self.BEANS_EVENT_MEMBER_COL},
            {self.BEANS_EVENT_TYPE_COL},
            {self.BEANS_EVENT_VALUE_COL})
            VALUES (?, ?, ?, ?);
        '''
        task = (event_id, event.get_member(), event.get_beans_event_type(), event.get_value())
        
        return self.__query_insert(command, task)
    
    def __create_inventory_event(self, event_id: int, event: InventoryEvent) -> int:
        command = f'''
            INSERT INTO {self.INVENTORY_EVENT_TABLE} (
            {self.INVENTORY_EVENT_ID_COL},
            {self.INVENTORY_EVENT_MEMBER_COL},
            {self.INVENTORY_EVENT_ITEM_TYPE_COL},
            {self.INVENTORY_EVENT_BEANS_EVENT_COL},
            {self.INVENTORY_EVENT_AMOUNT_COL})
            VALUES (?, ?, ?, ?, ?);
        '''
        task = (event_id, event.get_member_id(), event.get_item_type(), event.get_beans_event_id(), event.get_amount())
        
        return self.__query_insert(command, task)
    
    def __create_loot_box_event(self, event_id: int, event: LootBoxEvent) -> int:
        command = f'''
            INSERT INTO {self.LOOTBOX_EVENT_TABLE} (
            {self.LOOTBOX_EVENT_ID_COL},
            {self.LOOTBOX_EVENT_LOOTBOX_ID_COL},
            {self.LOOTBOX_EVENT_MEMBER_COL},
            {self.LOOTBOX_EVENT_TYPE_COL})
            VALUES (?, ?, ?, ?);
        '''
        task = (event_id, event.get_loot_box_id(), event.get_member_id(), event.get_loot_box_event_type())
        
        return self.__query_insert(command, task)
    
    def log_event(self, event: BotEvent) -> int:
        event_id = self.__create_base_event(event)
        
        if event_id is None:
            self.logger.error("DB","Event creation error, id was NoneType")
            return None
        
        match event.get_type():
            case EventType.INTERACTION:
                return self.__create_interaction_event(event_id, event)
            case EventType.JAIL:
                return self.__create_jail_event(event_id, event)
            case EventType.TIMEOUT:
                return self.__create_timeout_event(event_id, event)
            case EventType.QUOTE:
                return self.__create_quote_event(event_id, event)
            case EventType.SPAM:
                return self.__create_spam_event(event_id, event)
            case EventType.BEANS:
                return self.__create_beans_event(event_id, event)
            case EventType.INVENTORY:
                return self.__create_inventory_event(event_id, event)
            case EventType.LOOTBOX:
                return self.__create_loot_box_event(event_id, event)
                
    def log_quote(self, quote: Quote) -> int:
        command = f'''
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
        '''
        task = (
            quote.get_guild_id(),
            quote.get_member(), 
            quote.get_member_name(), 
            quote.get_saved_by(), 
            quote.get_message_id(), 
            quote.get_channel_id(), 
            quote.get_timestamp(), 
            quote.get_message_content(), 
        )
        
        return self.__query_insert(command, task)

    def log_lootbox(self, loot_box: LootBox) -> int:
        command = f'''
            INSERT INTO {self.LOOTBOX_TABLE} (
            {self.LOOTBOX_GUILD_COL},
            {self.LOOTBOX_MESSAGE_ID_COL},
            {self.LOOTBOX_ITEM_TYPE_COL},
            {self.LOOTBOX_BEANS_COL}) 
            VALUES (?, ?, ?, ?);
        '''
        task = (
            loot_box.get_guild_id(),
            loot_box.get_message_id(),
            loot_box.get_item_type(), 
            loot_box.get_beans()
        )
        
        return self.__query_insert(command, task)
    
    def log_bully_react(self, guild_id: int, user_id: int, target_id: int, emoji_type: EmojiType, emoji: discord.Emoji|str) -> int:
        command = f'''
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
        '''
        
        if emoji_type == EmojiType.CUSTOM:
            emoji = str(emoji.id)
        
        task = (
            guild_id,
            user_id,
            target_id,
            emoji_type.value,
            emoji
        )
        
        return self.__query_insert(command, task)
    
    def get_bully_react(self, guild_id: int, user_id: int) -> Tuple[int,discord.Emoji|str]:
        command = f'''
            SELECT * FROM {self.BULLY_REACT_TABLE}
            WHERE {self.BULLY_REACT_GUILD_COL} = ? 
            AND {self.BULLY_REACT_MEMBER_COL} = ? LIMIT 1;
        '''
        task = (guild_id, user_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None, None
        
        emoji = rows[0][self.BULLY_REACT_EMOJI_VALUE_COL]
        if rows[0][self.BULLY_REACT_EMOJI_TYPE_COL] == EmojiType.CUSTOM.value:
            emoji = discord.utils.get(self.bot.emojis, id=int(emoji))
        
        return rows[0][self.BULLY_REACT_TARGET_COL], emoji
    
    def log_custom_color(self, guild_id: int, user_id: int, color: str) -> int:
        command = f'''
            INSERT INTO {self.CUSTOM_COLOR_TABLE} ({self.CUSTOM_COLOR_GUILD_COL}, {self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_COLOR_COL}) 
            VALUES (?, ?, ?) 
            ON CONFLICT({self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_GUILD_COL}) 
            DO UPDATE SET {self.CUSTOM_COLOR_COLOR_COL}=excluded.{self.CUSTOM_COLOR_COLOR_COL};
        '''
        task = (
            guild_id,
            user_id,
            color
        )
        
        return self.__query_insert(command, task)
    
    def get_custom_color(self, guild_id: int, user_id: int) -> str:
        command = f'''
            SELECT * FROM {self.CUSTOM_COLOR_TABLE}
            WHERE {self.CUSTOM_COLOR_MEMBER_COL} = ? 
            AND {self.CUSTOM_COLOR_GUILD_COL} = ? LIMIT 1;
        '''
        task = (user_id, guild_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        
        return rows[0][self.CUSTOM_COLOR_COLOR_COL]
    
    def log_custom_role(self, guild_id: int, user_id: int, role_id: int) -> int:
        command = f'''
            INSERT INTO {self.CUSTOM_COLOR_TABLE} ({self.CUSTOM_COLOR_GUILD_COL}, {self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_ROLE_COL}) 
            VALUES (?, ?, ?) 
            ON CONFLICT({self.CUSTOM_COLOR_MEMBER_COL}, {self.CUSTOM_COLOR_GUILD_COL}) 
            DO UPDATE SET {self.CUSTOM_COLOR_ROLE_COL}=excluded.{self.CUSTOM_COLOR_ROLE_COL}
            WHERE excluded.{self.CUSTOM_COLOR_ROLE_COL} IS NOT NULL ;
        '''
        task = (
            guild_id,
            user_id,
            role_id
        )
        
        return self.__query_insert(command, task)
    
    def get_custom_role(self, guild_id: int, user_id: int) -> int:
        command = f'''
            SELECT * FROM {self.CUSTOM_COLOR_TABLE}
            WHERE {self.CUSTOM_COLOR_MEMBER_COL} = ? 
            AND {self.CUSTOM_COLOR_GUILD_COL} = ? LIMIT 1;
        '''
        task = (user_id, guild_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        
        return rows[0][self.CUSTOM_COLOR_ROLE_COL]
    
    def fix_quote(self, quote: Quote, channel_id: int) -> int:
        command = f'''
            UPDATE {self.QUOTE_TABLE} 
            SET {self.QUOTE_CHANNEL_COL} = ?
            WHERE {self.QUOTE_ID_COL} = ?;
        '''
        task = (channel_id, quote.get_id())
        
        return self.__query_insert(command, task)
    
    def increment_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        command = f'''
            INSERT INTO {self.TIMEOUT_TRACKER_TABLE} ({self.TIMEOUT_TRACKER_GUILD_ID_COL}, {self.TIMEOUT_TRACKER_MEMBER_COL}, {self.TIMEOUT_TRACKER_COUNT_COL}) 
            VALUES (?, ?, 1) 
            ON CONFLICT({self.TIMEOUT_TRACKER_GUILD_ID_COL}, {self.TIMEOUT_TRACKER_MEMBER_COL}) 
            DO UPDATE SET {self.TIMEOUT_TRACKER_COUNT_COL} = {self.TIMEOUT_TRACKER_COUNT_COL} + 1;
        '''
        task = (guild_id, user_id)
        
        return self.__query_insert(command, task)
    
    def reset_timeout_tracker(self, guild_id: int, user_id: int) -> int:
        command = f'''
            UPDATE {self.TIMEOUT_TRACKER_TABLE} 
            SET {self.TIMEOUT_TRACKER_COUNT_COL} = 0
            WHERE {self.TIMEOUT_TRACKER_GUILD_ID_COL} = ? 
            AND {self.TIMEOUT_TRACKER_MEMBER_COL} = ? ;
        '''
        task = (guild_id, user_id)
        
        return self.__query_insert(command, task)
    
    def get_timeout_tracker_count(self, guild_id: int, user_id: int) -> int:
        command = f'''
            SELECT * FROM {self.TIMEOUT_TRACKER_TABLE}
            WHERE {self.TIMEOUT_TRACKER_GUILD_ID_COL} = ? 
            AND {self.TIMEOUT_TRACKER_MEMBER_COL} = ? LIMIT 1;
        '''
        task = (guild_id, user_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0 
        
        return rows[0][self.TIMEOUT_TRACKER_COUNT_COL]
    
    def log_jail_sentence(self, jail: UserJail) -> UserJail:
        command = f'''
            INSERT INTO {self.JAIL_TABLE} (
            {self.JAIL_GUILD_ID_COL},
            {self.JAIL_MEMBER_COL},
            {self.JAIL_JAILED_ON_COL}) 
            VALUES (?, ?, ?);
        '''
        task = (jail.get_guild_id(), jail.get_member_id(), jail.get_jailed_on_timestamp())

        insert_id = self.__query_insert(command, task)
        return UserJail.from_jail(jail, jail_id=insert_id)
    
    def log_jail_release(self, jail_id: int, released_on: int) -> int:
        command = f'''
            UPDATE {self.JAIL_TABLE} 
            SET {self.JAIL_RELEASED_ON_COL} = ?
            WHERE {self.JAIL_ID_COL} = ?;
        '''
        task = (released_on, jail_id)
        
        return self.__query_insert(command, task)
            
    def get_active_jails(self) -> List[UserJail]:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        '''
        rows = self.__query_select(command)
        
        return [UserJail.from_db_row(row) for row in rows]
    
    def get_jail(self, jail_id: int) -> UserJail:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_ID_COL} = {int(jail_id)}
            LIMIT 1;
        '''
        rows = self.__query_select(command)
        
        if rows and len(rows) < 1:
            return None 
        
        return UserJail.from_db_row(rows) 
        
    def get_jails_by_guild(self, guild_id: int) -> List[UserJail]:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [UserJail.from_db_row(row) for row in rows]
    
    def get_active_jails_by_guild(self, guild_id: int) -> List[UserJail]:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_GUILD_ID_COL} = {int(guild_id)}
            AND {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [UserJail.from_db_row(row) for row in rows]
    
    def get_active_jails_by_member(self, guild_id: int, user_id: int) -> List[UserJail]:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_MEMBER_COL} = ?
            AND {self.JAIL_GUILD_ID_COL} = ?
            AND {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        '''
        task = (user_id, guild_id)
        rows = self.__query_select(command, task)
        if not rows: 
            return []
        return [UserJail.from_db_row(row) for row in rows]
    
    def get_jail_events_by_jail(self, jail_id: int) -> List[JailEvent]:
        command = f'''
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            WHERE {self.JAIL_EVENT_JAILREFERENCE_COL} = {int(jail_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [JailEvent.from_db_row(row) for row in rows]

    def get_jail_events_by_user(self, user_id: int) -> List[JailEvent]:
        command = f'''
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            AND {self.JAIL_EVENT_BY_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [JailEvent.from_db_row(row) for row in rows]
         
    def get_jail_events_affecting_user(self, user_id: int) -> List[JailEvent]:
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            INNER JOIN {self.JAIL_EVENT_TABLE} ON {self.JAIL_TABLE}.{self.JAIL_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_ID_COL}
            WHERE {self.JAIL_TABLE}.{self.JAIL_MEMBER_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [JailEvent.from_db_row(row) for row in rows]
        
    def get_jail_events_by_guild(self, guild_id: int) -> Dict[UserJail,List[JailEvent]]:
        jails = self.get_jails_by_guild(guild_id)
        output = {}
        for jail in jails:
            output[jail] = self.get_jail_events_by_jail(jail.get_id())
        
        return output
             
    def get_timeout_events_by_user(self, user_id: int) -> List[TimeoutEvent]:
        command = f'''
            SELECT * FROM {self.TIMEOUT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.TIMEOUT_EVENT_TABLE}.{self.TIMEOUT_EVENT_ID_COL}
            WHERE {self.TIMEOUT_EVENT_MEMBER_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [TimeoutEvent.from_db_row(row) for row in rows]
    
    def get_timeout_events_by_guild(self, guild_id: int) -> List[TimeoutEvent]:
        command = f'''
            SELECT * FROM {self.TIMEOUT_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.TIMEOUT_EVENT_TABLE}.{self.TIMEOUT_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [TimeoutEvent.from_db_row(row) for row in rows]

    def get_spam_events_by_user(self, user_id: int) -> List[SpamEvent]:
        command = f'''
            SELECT * FROM {self.SPAM_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.SPAM_EVENT_TABLE}.{self.SPAM_EVENT_ID_COL}
            WHERE {self.SPAM_EVENT_MEMBER_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [SpamEvent.from_db_row(row) for row in rows]
    
    def get_spam_events_by_guild(self, guild_id: int) -> List[SpamEvent]:
        command = f'''
            SELECT * FROM {self.SPAM_EVENT_TABLE}
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.SPAM_EVENT_TABLE}.{self.SPAM_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [SpamEvent.from_db_row(row) for row in rows]
    
    def get_interaction_events_by_user(self, user_id: int) -> List[InteractionEvent]:
        command = f'''
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.INTERACTION_EVENT_FROM_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]
        
    def get_interaction_events_affecting_user(self, user_id: int) -> List[InteractionEvent]:
        command = f'''
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.INTERACTION_EVENT_TO_COL} = {int(user_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]
    
    def get_guild_interaction_events(self, guild_id: int) -> List[InteractionEvent]:
        command = f'''
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INTERACTION_EVENT_TABLE}.{self.INTERACTION_EVENT_ID_COL}
            WHERE {self.EVENT_TABLE}.{self.EVENT_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]
    
    def get_random_quote(self, guild_id: int) -> Quote:
        command = f''' 
            SELECT * FROM {self.QUOTE_TABLE} 
            WHERE {self.QUOTE_TABLE}.{self.QUOTE_GUILD_COL} = {int(guild_id)}
            ORDER BY RANDOM() LIMIT 1;
        '''
        rows = self.__query_select(command)
        if not rows: 
            return None
        return Quote.from_db_row(rows[0])
    
    def get_random_quote_by_user(self, guild_id: int, user_id: int) -> Quote:
        command = f''' 
            SELECT * FROM {self.QUOTE_TABLE} 
            WHERE {self.QUOTE_TABLE}.{self.QUOTE_GUILD_COL} = ?
            AND {self.QUOTE_TABLE}.{self.QUOTE_MEMBER_COL} = ?
            ORDER BY RANDOM() LIMIT 1;
        '''
        task = (guild_id, user_id)
        rows = self.__query_select(command,task)
        if not rows: 
            return None
        return Quote.from_db_row(rows[0])

    def get_loot_box_by_message_id(self, guild_id: int, message_id: int) -> LootBox:
        command = f''' 
            SELECT * FROM {self.LOOTBOX_TABLE} 
            WHERE {self.LOOTBOX_MESSAGE_ID_COL} = ?
            AND {self.LOOTBOX_GUILD_COL} = ?
            LIMIT 1;
        '''
        task = (message_id, guild_id)
        rows = self.__query_select(command,task)
        if not rows: 
            return None
        return LootBox.from_db_row(rows[0])
    
    def get_last_loot_box_event(self, guild_id: int):
        command = f'''
            SELECT * FROM {self.LOOTBOX_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            WHERE {self.LOOTBOX_EVENT_TYPE_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC LIMIT 1;
        '''
        task = (LootBoxEventType.DROP.value, guild_id)
        rows = self.__query_select(command, task)
        if not rows: 
            return None
        return LootBoxEvent.from_db_row(rows[0])
    
    def get_member_beans(self, guild_id: int, user_id: int) -> int:
        command = f'''
            SELECT SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?;
        '''
        task = (user_id, guild_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0
        output = rows[0][f'SUM({self.BEANS_EVENT_VALUE_COL})']
        return output if output is not None else 0
    
    def get_guild_beans(self, guild_id: int) -> Dict[int, int]:
        command = f'''
            SELECT {self.BEANS_EVENT_MEMBER_COL}, SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = {int(guild_id)}
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        '''
        
        rows = self.__query_select(command)
        if not rows or len(rows) < 1:
            return {}
        
        output = { row[self.BEANS_EVENT_MEMBER_COL]: row[f'SUM({self.BEANS_EVENT_VALUE_COL})'] for row in rows }
        
        return output
    
    def get_guild_beans_rankings(self, guild_id: int) -> Dict[int, int]:
        command = f'''
            SELECT {self.BEANS_EVENT_MEMBER_COL}, SUM({self.BEANS_EVENT_VALUE_COL}) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = ?
            WHERE {self.BEANS_EVENT_TYPE_COL} != ?
            GROUP BY {self.BEANS_EVENT_MEMBER_COL};
        '''
        task = (guild_id, BeansEventType.SHOP_PURCHASE.value)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}
        
        return { row[self.BEANS_EVENT_MEMBER_COL]: row[f'SUM({self.BEANS_EVENT_VALUE_COL})'] for row in rows }
        
    
    def get_lootbox_purchases_by_guild(self, guild_id: int) -> Dict[int,int]:
        
        command = f'''
            SELECT {self.LOOTBOX_EVENT_MEMBER_COL}, COUNT({self.LOOTBOX_EVENT_TYPE_COL}) FROM {self.LOOTBOX_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.LOOTBOX_EVENT_TABLE}.{self.LOOTBOX_EVENT_ID_COL}
            AND {self.EVENT_GUILD_ID_COL} = ?
            WHERE {self.LOOTBOX_EVENT_TYPE_COL} = ?
            GROUP BY {self.LOOTBOX_EVENT_MEMBER_COL};
        '''
        task = (guild_id, LootBoxEventType.BUY.value)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}
        
        return{ row[self.LOOTBOX_EVENT_MEMBER_COL]: row[f'COUNT({self.LOOTBOX_EVENT_TYPE_COL})'] for row in rows }
    
    def get_beans_daily_gamba_count(self, guild_id: int, user_id: int, type: BeansEventType, min_value: int, date: int) -> int:
        command = f'''
            SELECT COUNT(*) FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.BEANS_EVENT_TYPE_COL} = ?
            AND ABS({self.BEANS_EVENT_VALUE_COL}) >= ?
            AND {self.EVENT_TIMESTAMP_COL} >= ?;
        '''
        task = (user_id, guild_id, type, min_value, date)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return 0
        
        return rows[0][f'COUNT(*)']
    
    def get_last_beans_event(self, guild_id: int, user_id: int, type: BeansEventType) -> BeansEvent:
        command = f'''
            SELECT * FROM {self.BEANS_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.BEANS_EVENT_TABLE}.{self.BEANS_EVENT_ID_COL}
            WHERE {self.BEANS_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            AND {self.BEANS_EVENT_TYPE_COL} = ?
            ORDER BY {self.EVENT_TIMESTAMP_COL} DESC LIMIT 1;
        '''
        task = (user_id, guild_id, type)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return None
        return BeansEvent.from_db_row(rows[0])
    
    def get_lottery_data(self, guild_id: int) -> Dict[int,int]:     
        command = f'''
            SELECT {self.INVENTORY_EVENT_MEMBER_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = ?
            AND {self.INVENTORY_EVENT_ITEM_TYPE_COL} = ?
            GROUP BY {self.INVENTORY_EVENT_MEMBER_COL};
        '''
        task = (guild_id, ItemType.LOTTERY_TICKET)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return {}
        rows = { row[self.INVENTORY_EVENT_MEMBER_COL]: row[f'SUM({self.INVENTORY_EVENT_AMOUNT_COL})'] for row in rows if row[f'SUM({self.INVENTORY_EVENT_AMOUNT_COL})'] > 0}
        return rows
    
    def get_inventories_by_guild(self, guild_id: int) -> List[UserInventory]: 
        command = f'''
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, {self.INVENTORY_EVENT_MEMBER_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.EVENT_GUILD_ID_COL} = {int(guild_id)}
            GROUP BY {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        '''
        
        rows = self.__query_select(command)
        if not rows or len(rows) < 1:
            return []
        
        transformed = {}
        for row in rows:
            user_id = row[self.INVENTORY_EVENT_MEMBER_COL]
            item_type = row[self.INVENTORY_EVENT_ITEM_TYPE_COL]
            amount = row[f'SUM({self.INVENTORY_EVENT_AMOUNT_COL})']
            if amount <= 0:
                continue
            if user_id not in transformed.keys():
                transformed[user_id] = {item_type: amount}
            else:
                transformed[user_id][item_type] = amount
                
        inventories = []
        for user_id, items in transformed.items():
            inventories.append(UserInventory(guild_id, user_id, items))
        
        return inventories
    
    def get_inventory_by_user(self, guild_id: int, user_id: int) -> UserInventory: 
        command = f'''
            SELECT {self.INVENTORY_EVENT_ITEM_TYPE_COL}, SUM({self.INVENTORY_EVENT_AMOUNT_COL}) FROM {self.INVENTORY_EVENT_TABLE} 
            INNER JOIN {self.EVENT_TABLE} 
            ON {self.EVENT_TABLE}.{self.EVENT_ID_COL} = {self.INVENTORY_EVENT_TABLE}.{self.INVENTORY_EVENT_ID_COL}
            WHERE {self.INVENTORY_EVENT_MEMBER_COL} = ?
            AND {self.EVENT_GUILD_ID_COL} = ?
            GROUP BY {self.INVENTORY_EVENT_ITEM_TYPE_COL};
        '''
        task = (user_id, guild_id)
        
        rows = self.__query_select(command, task)
        if not rows or len(rows) < 1:
            return UserInventory(guild_id, user_id, {})
        
        items = { row[self.INVENTORY_EVENT_ITEM_TYPE_COL]: row[f'SUM({self.INVENTORY_EVENT_AMOUNT_COL})'] for row in rows if row[f'SUM({self.INVENTORY_EVENT_AMOUNT_COL})'] > 0}
        return UserInventory(guild_id, user_id, items)