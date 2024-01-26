from typing import Dict, List
import json
import sqlite3
from sqlite3 import Error, OperationalError
import traceback

from BotLogger import BotLogger
from datalayer.UserJail import UserJail
from datalayer.Quote import Quote
from events.BotEvent import BotEvent
from events.EventType import EventType
from events.InteractionEvent import InteractionEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.QuoteEvent import QuoteEvent
from events.TimeoutEvent import TimeoutEvent


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
    OLD_SETTINGS_GUILD_ID_COL = 'guild_id'
    OLD_SETTINGS_MODULE_COL = 'module'
    OLD_SETTINGS_KEY_COL = 'key'
    OLD_SETTINGS_VALUE_COL = 'value'
    
    settings_dict = {
        OLD_SETTINGS_GUILD_ID_COL : SETTINGS_GUILD_ID_COL,
        OLD_SETTINGS_MODULE_COL : SETTINGS_MODULE_COL,
        OLD_SETTINGS_KEY_COL : SETTINGS_KEY_COL,
        OLD_SETTINGS_VALUE_COL : SETTINGS_VALUE_COL
    }
    
    
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
    OLD_JAIL_ID_COL = 'id'
    OLD_JAIL_GUILD_ID_COL = 'guild_id'
    OLD_JAIL_MEMBER_COL = 'member'
    OLD_JAIL_JAILED_ON_COL = 'jailed_on'
    OLD_JAIL_RELEASED_ON_COL = 'released_on'
    
    jail_dict = {
        OLD_JAIL_ID_COL : JAIL_ID_COL,
        OLD_JAIL_GUILD_ID_COL : JAIL_GUILD_ID_COL,
        OLD_JAIL_MEMBER_COL : JAIL_MEMBER_COL,
        OLD_JAIL_JAILED_ON_COL : JAIL_JAILED_ON_COL,
        OLD_JAIL_RELEASED_ON_COL : JAIL_RELEASED_ON_COL
    }
    
    
    EVENT_TABLE = 'events'
    EVENT_ID_COL = 'evnt_id'
    EVENT_TIMESTAMP_COL = 'evnt_timestamp'
    EVEN_GUILD_ID_COL = 'evnt_guild_id'
    EVENT_TYPE_COL = 'evnt_type'
    CREATE_EVENT_TABLE = f'''
    CREATE TABLE if not exists {EVENT_TABLE} (
        {EVENT_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT, 
        {EVENT_TIMESTAMP_COL} INTEGER,
        {EVEN_GUILD_ID_COL} INTEGER,
        {EVENT_TYPE_COL} TEXT
    );'''
    OLD_EVENT_ID_COL = 'event_id'
    OLD_EVENT_TIMESTAMP_COL = 'timestamp'
    OLD_EVEN_GUILD_ID_COL = 'guild_id'
    OLD_EVENT_TYPE_COL = 'type'

    event_dict = {
        OLD_EVENT_ID_COL : EVENT_ID_COL,
        OLD_EVENT_TIMESTAMP_COL : EVENT_TIMESTAMP_COL,
        OLD_EVEN_GUILD_ID_COL : EVEN_GUILD_ID_COL,
        OLD_EVENT_TYPE_COL : EVENT_TYPE_COL
    }
    
    
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
    OLD_INTERACTION_EVENT_ID_COL = 'id'
    OLD_INTERACTION_EVENT_TYPE_COL= 'type'
    OLD_INTERACTION_EVENT_FROM_COL = 'from_member'
    OLD_INTERACTION_EVENT_TO_COL = 'to_member'
    
    interaction_event_dict = {
        OLD_INTERACTION_EVENT_ID_COL : INTERACTION_EVENT_ID_COL,
        OLD_INTERACTION_EVENT_TYPE_COL : INTERACTION_EVENT_TYPE_COL,
        OLD_INTERACTION_EVENT_FROM_COL : INTERACTION_EVENT_FROM_COL,
        OLD_INTERACTION_EVENT_TO_COL : INTERACTION_EVENT_TO_COL
    }
    
    
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
    OLD_JAIL_EVENT_ID_COL = 'id'
    OLD_JAIL_EVENT_TYPE_COL = 'type'
    OLD_JAIL_EVENT_BY_COL = 'by'
    OLD_JAIL_EVENT_DURATION_COL = 'duration'
    OLD_JAIL_EVENT_JAILREFERENCE_COL = 'sentence_id'
    
    jail_event_dict = {
        OLD_JAIL_EVENT_ID_COL : JAIL_EVENT_ID_COL,
        OLD_JAIL_EVENT_TYPE_COL : JAIL_EVENT_TYPE_COL,
        OLD_JAIL_EVENT_BY_COL : JAIL_EVENT_BY_COL,
        OLD_JAIL_EVENT_DURATION_COL : JAIL_EVENT_DURATION_COL,
        OLD_JAIL_EVENT_JAILREFERENCE_COL : JAIL_EVENT_JAILREFERENCE_COL
    }
    
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
    OLD_TIMEOUT_EVENT_ID_COL = 'id'
    OLD_TIMEOUT_EVENT_MEMBER_COL = 'member'
    OLD_TIMEOUT_EVENT_DURATION_COL = 'duration'
    
    timeout_event_dict = {
        OLD_TIMEOUT_EVENT_ID_COL : TIMEOUT_EVENT_ID_COL,
        OLD_TIMEOUT_EVENT_MEMBER_COL : TIMEOUT_EVENT_MEMBER_COL,
        OLD_TIMEOUT_EVENT_DURATION_COL : TIMEOUT_EVENT_DURATION_COL
    }
    
    
    QUOTE_TABLE = 'quotes'
    QUOTE_ID_COL = 'quot_id'
    QUOTE_GUILD_COL = 'quot_guild_id'
    QUOTE_MEMBER_COL = 'quot_member_id'
    QUOTE_MEMBER_NAME_COL = 'quot_member_name'
    QUOTE_SAVED_BY_COL = 'quot_saved_by'
    QUOTE_MESSAGE_COL = 'quot_message_id'
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
        {QUOTE_TIMESTAMP_COL} INTEGER, 
        {QUOTE_TEXT_COL} TEXT
    );'''
    OLD_QUOTE_ID_COL = 'id'
    OLD_QUOTE_GUILD_COL = 'guild_id'
    OLD_QUOTE_MEMBER_COL = 'member_id'
    OLD_QUOTE_MEMBER_NAME_COL = 'member_name'
    OLD_QUOTE_SAVED_BY_COL = 'saved_by'
    OLD_QUOTE_MESSAGE_COL = 'message_id'
    OLD_QUOTE_TIMESTAMP_COL = 'timestamp'
    OLD_QUOTE_TEXT_COL = 'message_content'
    
    quote_dict = {
        OLD_QUOTE_ID_COL : QUOTE_ID_COL,
        OLD_QUOTE_GUILD_COL : QUOTE_GUILD_COL,
        OLD_QUOTE_MEMBER_COL : QUOTE_MEMBER_COL,
        OLD_QUOTE_MEMBER_NAME_COL : QUOTE_MEMBER_NAME_COL,
        OLD_QUOTE_SAVED_BY_COL : QUOTE_SAVED_BY_COL,
        OLD_QUOTE_MESSAGE_COL : QUOTE_MESSAGE_COL,
        OLD_QUOTE_TIMESTAMP_COL : QUOTE_TIMESTAMP_COL,
        OLD_QUOTE_TEXT_COL : QUOTE_TEXT_COL
    }
    
    
    
    QUOTE_EVENT_TABLE = 'quoteevents'
    QUOTE_EVENT_ID_COL = 'quev_id'
    QUOTE_EVENT_REF_COL = 'quev_quote_id'
    CREATE_QUOTE_EVENT_TABLE = f'''
    CREATE TABLE if not exists {QUOTE_EVENT_TABLE} (
        {QUOTE_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {QUOTE_EVENT_REF_COL} INTEGER REFERENCES {QUOTE_TABLE} ({QUOTE_ID_COL}),
        PRIMARY KEY ({QUOTE_EVENT_ID_COL})
    );'''
    OLD_QUOTE_EVENT_ID_COL = 'id'
    OLD_QUOTE_EVENT_REF_COL = 'quote_id'
    
    quote_event_dict = {
        OLD_QUOTE_EVENT_ID_COL : QUOTE_EVENT_ID_COL,
        OLD_QUOTE_EVENT_REF_COL : QUOTE_EVENT_REF_COL
    }
    
    
    def __init__(self, logger: BotLogger, db_file: str):
        
        self.conn = None
        self.logger = logger
        
        
        lst = {
            self.SETTINGS_TABLE: self.settings_dict,
            self.EVENT_TABLE: self.event_dict,
            self.JAIL_TABLE: self.jail_dict,
            self.JAIL_EVENT_TABLE: self.jail_event_dict,
            self.INTERACTION_EVENT_TABLE: self.interaction_event_dict,
            self.TIMEOUT_EVENT_TABLE: self.timeout_event_dict
        }
        
        
        try:
            self.conn = sqlite3.connect(db_file)
            
            c = self.conn.cursor()
            
            c.execute(f"SELECT {self.SETTINGS_GUILD_ID_COL} FROM {self.SETTINGS_TABLE};")
            c.close()
        except OperationalError as e:
            
            self.conn = sqlite3.connect(db_file)
            self.logger.log("DB",f'Loaded DB version {sqlite3.version} from {db_file}.')
            
            c = self.conn.cursor()
            
            for table, item in lst.items():
                self.logger.log("DB",f'--{table}--')
                for old, new in item.items():
                    command = f'ALTER TABLE {table} RENAME COLUMN "{old}" TO "{new}"'
                    self.logger.log("DB",f'{command} : {old} -> {new}')
                    c.execute(command)
            
            c.close()
        
        
        try:
            self.conn = sqlite3.connect(db_file)
            self.logger.log("DB",f'Loaded DB version {sqlite3.version} from {db_file}.')
            
            c = self.conn.cursor()
            
            c.execute(self.CREATE_SETTINGS_TABLE)
            c.execute(self.CREATE_JAIL_TABLE)
            c.execute(self.CREATE_EVENT_TABLE)
            c.execute(self.CREATE_QUOTE_TABLE)
            c.execute(self.CREATE_INTERACTION_EVENT_TABLE)
            c.execute(self.CREATE_JAIL_EVENT_TABLE)
            c.execute(self.CREATE_TIMEOUT_EVENT_TABLE)
            c.execute(self.CREATE_QUOTE_EVENT_TABLE)
            c.close()
            
        except Error as e:
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

    def get_all_settings(self):
        
        command = f'SELECT * FROM {self.SETTINGS_TABLE};'
        try:
            c = self.conn.cursor()
            c.execute(command,)
            rows = c.fetchall()
        
            output = []
            
            for row in rows:
                new_row = {
                    self.SETTINGS_GUILD_ID_COL : row[0],
                    self.SETTINGS_MODULE_COL : row[1],
                    self.SETTINGS_KEY_COL : row[2],
                    self.SETTINGS_VALUE_COL : json.loads(row[3])
                }
                output.append(new_row)
            
            return output
            
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_exc()
            return None 
                
    def get_setting(self, guild_id: int, module: str, key: str):
        
        command = f'''
            SELECT * FROM {self.SETTINGS_TABLE} 
            WHERE {self.SETTINGS_GUILD_ID_COL}=? AND {self.SETTINGS_MODULE_COL}=? AND {self.SETTINGS_KEY_COL}=? 
            LIMIT 1;
        '''
        
        task = (int(guild_id), str(module), str(key))
        try:
            c = self.conn.cursor()
            c.execute(command, task)
            row = c.fetchone()
            
            if row is None:
                return None
                
            return json.loads(row[3])
            
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_exc()
            return None
    
    def update_setting(self, guild_id: int, module: str, key: str, value):
        try:
            value = json.dumps(value)
            
            command = f'INSERT INTO {self.SETTINGS_TABLE} ({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}, {self.SETTINGS_VALUE_COL}) VALUES (?, ?, ?, ?) ON CONFLICT({self.SETTINGS_GUILD_ID_COL}, {self.SETTINGS_MODULE_COL}, {self.SETTINGS_KEY_COL}) DO UPDATE SET {self.SETTINGS_VALUE_COL}=excluded.{self.SETTINGS_VALUE_COL};'
            task = (int(guild_id), str(module), str(key), value)
        
            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
            traceback.print_exc()
    
    def __create_base_event(self, event: BotEvent) -> int:
        
        command = f'''
                INSERT INTO {self.EVENT_TABLE} (
                {self.EVENT_TIMESTAMP_COL}, 
                {self.EVEN_GUILD_ID_COL}, 
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
        task = (event_id, event.get_jail_event_type(), event.get_jailed_by(), event.get_duration(), event.get_jail_id())

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
                
    def log_quote(self, quote: Quote) -> int:
        
        command = f'''
            INSERT INTO {self.QUOTE_TABLE} (
            {self.QUOTE_GUILD_COL},
            {self.QUOTE_MEMBER_COL},
            {self.QUOTE_MEMBER_NAME_COL},
            {self.QUOTE_SAVED_BY_COL},
            {self.QUOTE_MESSAGE_COL},
            {self.QUOTE_TIMESTAMP_COL},
            {self.QUOTE_TEXT_COL}) 
            VALUES (?, ?, ?, ?, ?, ?, ?);
        '''
        task = (
            quote.get_guild_id(),
            quote.get_member(), 
            quote.get_member_name(), 
            quote.get_saved_by(), 
            quote.get_message_id(), 
            quote.get_timestamp(), 
            quote.get_message_content(), 
        )
        
        return self.__query_insert(command, task)
        
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
            WHERE {self.JAIL_GUILD_ID_COL} = {int(guild_id)}
        '''
        rows = self.__query_select(command)
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
            WHERE {self.EVENT_TABLE}.{self.EVEN_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [TimeoutEvent.from_db_row(row) for row in rows]
    
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
            WHERE {self.EVENT_TABLE}.{self.EVEN_GUILD_ID_COL} = {int(guild_id)};
        '''
        rows = self.__query_select(command)
        if not rows: 
            return []
        return [InteractionEvent.from_db_row(row) for row in rows]