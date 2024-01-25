import json
import sqlite3
from sqlite3 import Error

from BotLogger import BotLogger
from events.BotEvent import BotEvent
from events.EventType import EventType
from events.InteractionEvent import InteractionEvent
from events.JailEvent import JailEvent
from events.JailEventType import JailEventType
from events.TimeoutEvent import TimeoutEvent


class Database():    
    
    SETTINGS_TABLE = 'guildsettings'
    SETTINGS_GUILD_ID_COL = 'guild_id'
    SETTINGS_MODULE_COL = 'module'
    SETTINGS_KEY_COL = 'key'
    SETTINGS_VALUE_COL = 'value'
    CREATE_SETTINGS_TABLE = f'''
    CREATE TABLE if not exists {SETTINGS_TABLE} (
        {SETTINGS_GUILD_ID_COL} INTEGER, 
        {SETTINGS_MODULE_COL} TEXT, 
        {SETTINGS_KEY_COL} TEXT, 
        {SETTINGS_VALUE_COL}, 
        PRIMARY KEY ({SETTINGS_GUILD_ID_COL}, {SETTINGS_MODULE_COL}, {SETTINGS_KEY_COL})
    );'''
    
    JAIL_TABLE = 'jail'
    JAIL_ID_COL = 'id'
    JAIL_GUILD_ID_COL = 'guild_id'
    JAIL_MEMBER_COL = 'member'
    JAIL_JAILED_ON_COL = 'jailed_on'
    JAIL_RELEASED_ON_COL = 'released_on'
    CREATE_JAIL_TABLE = f'''
    CREATE TABLE if not exists {JAIL_TABLE} (
        {JAIL_ID_COL}  INTEGER PRIMARY KEY AUTOINCREMENT,
        {JAIL_GUILD_ID_COL} INTEGER, 
        {JAIL_MEMBER_COL} INTEGER, 
        {JAIL_JAILED_ON_COL} INTEGER, 
        {JAIL_RELEASED_ON_COL} INTEGER
    );'''
    
    EVENT_TABLE = 'events'
    EVENT_ID_COL = 'event_id'
    EVENT_TIMESTAMP_COL = 'timestamp'
    EVEN_GUILD_ID_COL = 'guild_id'
    EVENT_TYPE_COL = 'type'
    CREATE_EVENT_TABLE = f'''
    CREATE TABLE if not exists {EVENT_TABLE} (
        {EVENT_ID_COL} INTEGER PRIMARY KEY AUTOINCREMENT, 
        {EVENT_TIMESTAMP_COL} INTEGER,
        {EVEN_GUILD_ID_COL} INTEGER,
        {EVENT_TYPE_COL} TEXT
    );'''
    

    INTERACTION_EVENT_TABLE = 'interactionevents'
    INTERACTION_EVENT_ID_COL = 'id'
    INTERACTION_EVENT_TYPE_COL= 'type'
    INTERACTION_EVENT_FROM_COL = 'from_member'
    INTERACTION_EVENT_TO_COL = 'to_member'
    CREATE_INTERACTION_EVENT_TABLE = f'''
    CREATE TABLE if not exists {INTERACTION_EVENT_TABLE} (
        {INTERACTION_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {INTERACTION_EVENT_TYPE_COL} TEXT, 
        {INTERACTION_EVENT_FROM_COL} INTEGER, 
        {INTERACTION_EVENT_TO_COL} INTEGER,
        PRIMARY KEY ({INTERACTION_EVENT_ID_COL})
    );'''
    
    JAIL_EVENT_TABLE = 'jailevents'
    JAIL_EVENT_ID_COL = 'id'
    JAIL_EVENT_TYPE_COL = 'type'
    JAIL_EVENT_BY_COL = 'by'
    JAIL_EVENT_DURATION_COL = 'duration'
    JAIL_EVENT_JAILREFERENCE_COL = 'sentence_id'
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
    TIMEOUT_EVENT_ID_COL = 'id'
    TIMEOUT_EVENT_MEMBER_COL = 'member'
    TIMEOUT_EVENT_DURATION_COL = 'duration'
    CREATE_TIMEOUT_EVENT_TABLE = f'''
    CREATE TABLE if not exists {TIMEOUT_EVENT_TABLE} (
        {TIMEOUT_EVENT_ID_COL} INTEGER REFERENCES {EVENT_TABLE} ({EVENT_ID_COL}),
        {TIMEOUT_EVENT_MEMBER_COL} INTEGER, 
        {TIMEOUT_EVENT_DURATION_COL} INTEGER,
        PRIMARY KEY ({TIMEOUT_EVENT_ID_COL})
    );'''
    
    
    def __init__(self, logger: BotLogger, db_file: str):
        
        self.conn = None
        self.logger = logger
        try:
            self.conn = sqlite3.connect(db_file)
            self.logger.log("DB",f'Loaded DB version {sqlite3.version} from {db_file}.')
            
            c = self.conn.cursor()
            
            c.execute(self.CREATE_SETTINGS_TABLE)
            c.execute(self.CREATE_JAIL_TABLE)
            c.execute(self.CREATE_EVENT_TABLE)
            c.execute(self.CREATE_INTERACTION_EVENT_TABLE)
            c.execute(self.CREATE_JAIL_EVENT_TABLE)
            c.execute(self.CREATE_TIMEOUT_EVENT_TABLE)
            c.close()
            
        except Error as e:
            self.logger.error("DB",e)

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
    
    def __create_base_event(self, event: BotEvent) -> int:
        try:
            command = f'''
                INSERT INTO {self.EVENT_TABLE} (
                {self.EVENT_TIMESTAMP_COL}, 
                {self.EVEN_GUILD_ID_COL}, 
                {self.EVENT_TYPE_COL}) 
                VALUES (?, ?, ?);
            '''
            task = (event.get_timestamp(), event.get_guild_id(), event.get_type())

            cur = self.conn.cursor()
            cur.execute(command, task)
            insert_id = cur.lastrowid
            
            self.conn.commit()
            
            return insert_id
        
        except Error as e:
            self.logger.error("DB",e)
            return None
    
    def __create_interaction_event(self, event_id: int, event: InteractionEvent):
        
        try:
            command = f'''
                INSERT INTO {self.INTERACTION_EVENT_TABLE} (
                {self.INTERACTION_EVENT_ID_COL},
                {self.INTERACTION_EVENT_TYPE_COL},
                {self.INTERACTION_EVENT_FROM_COL},
                {self.INTERACTION_EVENT_TO_COL}) 
                VALUES (?, ?, ?, ?);
            '''
            
            task = (event_id, event.get_interaction_type(), event.get_from_user(), event.get_to_user())

            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
    
    def __create_timeout_event(self, event_id: int, event: TimeoutEvent):
        
        try:
            command = f'''
                INSERT INTO {self.TIMEOUT_EVENT_TABLE} (
                {self.TIMEOUT_EVENT_ID_COL},
                {self.TIMEOUT_EVENT_MEMBER_COL},
                {self.TIMEOUT_EVENT_DURATION_COL})
                VALUES (?, ?, ?);
            '''
            
            task = (event_id, event.get_member(), event.get_duration())

            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
    
    def __create_jail_event(self, event_id: int, event: JailEvent):
        
        try:
            command = f'''
                INSERT INTO {self.JAIL_EVENT_TABLE} (
                {self.JAIL_EVENT_ID_COL},
                {self.JAIL_EVENT_TYPE_COL},
                {self.JAIL_EVENT_BY_COL},
                {self.JAIL_EVENT_DURATION_COL},
                {self.JAIL_EVENT_JAILREFERENCE_COL})
                VALUES (?, ?, ?, ?, ?);
            '''
            
            task = (event_id, event.get_jail_event_type(), event.get_jailed_by(), event.get_duration(), event.get_jail_reference())

            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
    
    def log_event(self, event: BotEvent):
        
        event_id = self.__create_base_event(event)
        
        if event_id is None:
            self.logger.error("DB","Event creation error, id was NoneType")
            return
        
        match event.get_type():
            case EventType.INTERACTION:
                self.__create_interaction_event(event_id, event)
            case EventType.JAIL:
                self.__create_jail_event(event_id, event)
            case EventType.TIMEOUT:
                self.__create_timeout_event(event_id, event)
        
    def log_jail_sentence(self, guild_id: int, member_id: int, jailed_on: int) -> int:
        
        try:
            command = f'''
                INSERT INTO {self.JAIL_TABLE} (
                {self.JAIL_GUILD_ID_COL},
                {self.JAIL_MEMBER_COL},
                {self.JAIL_JAILED_ON_COL}) 
                VALUES (?, ?, ?);
            '''
            
            task = (guild_id, member_id, jailed_on)

            cur = self.conn.cursor()
            cur.execute(command, task)
            insert_id = cur.lastrowid
            self.conn.commit()
            
            return insert_id
        
        except Error as e:
            self.logger.error("DB",e)
            return None
    
    def log_jail_release(self, jail_id: int, released_on: int):
        
        try:
            command = f'''
                UPDATE {self.JAIL_TABLE} 
                SET {self.JAIL_RELEASED_ON_COL} = ?
                WHERE {self.JAIL_ID_COL} = ?;
            '''
            
            task = (released_on, jail_id)

            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
            
        except Error as e:
            self.logger.error("DB",e)
            
    def get_active_jails(self):
        
        command = f'''
            SELECT * FROM {self.JAIL_TABLE} 
            WHERE {self.JAIL_RELEASED_ON_COL} IS NULL 
            OR {self.JAIL_RELEASED_ON_COL} = 0;
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command)
            rows = c.fetchall()
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
    
    def get_jail_events(self, jail_id: int):
        
        command = f'''
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            WHERE {self.JAIL_EVENT_JAILREFERENCE_COL} = {int(jail_id)};
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 

    def has_jail_event(self, jail_id: int, user_id: int, type: JailEventType):
        
        command = f'''
            SELECT * FROM {self.JAIL_EVENT_TABLE} 
            WHERE {self.JAIL_EVENT_JAILREFERENCE_COL} = ?
            AND {self.JAIL_EVENT_BY_COL} = ?
            AND {self.JAIL_EVENT_TYPE_COL} = ?
            LIMIT 1;
        '''
        
        task = (jail_id, user_id,type)
        
        try:
            c = self.conn.cursor()
            c.execute(command, task)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
         
    def get_user_jail_events(self, user_id: int):
        
        command = f'''
            SELECT {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL},
                   {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_TYPE_COL},
                   {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_DURATION_COL},
                   {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_BY_COL}
            FROM {self.JAIL_TABLE} 
            INNER JOIN {self.JAIL_EVENT_TABLE} ON {self.JAIL_TABLE}.{self.JAIL_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL}
            WHERE {self.JAIL_TABLE}.{self.JAIL_MEMBER_COL} = {int(user_id)};
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
        
    def get_user_jail_interaction_events(self, user_id: int):
        
        command = f'''
            SELECT {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL},
                   {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_TYPE_COL},
                   {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_DURATION_COL},
                   {self.JAIL_TABLE}.{self.JAIL_MEMBER_COL}
            FROM {self.JAIL_TABLE} 
            INNER JOIN {self.JAIL_EVENT_TABLE} ON {self.JAIL_TABLE}.{self.JAIL_ID_COL} = {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_JAILREFERENCE_COL}
            WHERE {self.JAIL_EVENT_TABLE}.{self.JAIL_EVENT_BY_COL} = {int(user_id)};
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
        
    def get_user_timeout_events(self, user_id: int):
        
        command = f'''
            SELECT * FROM {self.TIMEOUT_EVENT_TABLE}
            WHERE {self.TIMEOUT_EVENT_MEMBER_COL} = {int(user_id)};
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            return self.__parse_rows(rows, headings)
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
    
    def get_user_interaction_events(self, user_id: int):
        
        command_from = f'''
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            WHERE {self.INTERACTION_EVENT_FROM_COL} = {int(user_id)};
        '''
        
        command_to = f'''
            SELECT * FROM {self.INTERACTION_EVENT_TABLE} 
            WHERE {self.INTERACTION_EVENT_TO_COL} = {int(user_id)};
        '''
        
        try:
            c = self.conn.cursor()
            c.execute(command_from)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            from_rows =  self.__parse_rows(rows, headings)
            
            c = self.conn.cursor()
            c.execute(command_to)
            rows = c.fetchall()
            
            headings = [x[0] for x in c.description]
            to_rows =  self.__parse_rows(rows, headings)
            
            return {"out": from_rows, "in": to_rows}
            
        except Error as e:
            self.logger.error("DB",e)
            return None 