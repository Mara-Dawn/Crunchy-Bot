import json
import sqlite3
from sqlite3 import Error

from BotLogger import BotLogger


class Database():    
    
    SETTINGS_TABLE = 'guildsettings'
    
    GUILD_ID_COL = 'guild_id'
    MODULE_COL = 'module'
    KEY_COL = 'key'
    VALUE_COL = 'value'
    
    CREATE_GUILD_SETTINGS_TABLE = f'CREATE TABLE if not exists {SETTINGS_TABLE} ({GUILD_ID_COL} INTEGER, {MODULE_COL} TEXT, {KEY_COL} TEXT, {VALUE_COL}, PRIMARY KEY ({GUILD_ID_COL}, {MODULE_COL}, {KEY_COL}));'
    
    
    def __init__(self, logger: BotLogger, db_file: str):
        
        self.conn = None
        self.logger = logger
        try:
            self.conn = sqlite3.connect(db_file)
            self.logger.log("DB",f'Loaded DB version {sqlite3.version} from {db_file}.')
            
            c = self.conn.cursor()
            
            c.execute(self.CREATE_GUILD_SETTINGS_TABLE)
            c.close()
            
        except Error as e:
            self.logger.error("DB",e)
            
            
    def get_all_settings(self):
        
        command = f'SELECT * FROM {self.SETTINGS_TABLE};'
        try:
            c = self.conn.cursor()
            c.execute(command,)
            rows = c.fetchall()
        
            output = []
            
            for row in rows:
                new_row = {
                    self.GUILD_ID_COL : row[0],
                    self.MODULE_COL : row[1],
                    self.KEY_COL : row[2],
                    self.VALUE_COL : json.loads(row[3])
                }
                output.append(new_row)
            
            return output
            
        except Error as e:
            self.logger.error("DB",e)
            return None 
                
    def get_setting(self, guild_id: int, module: str, key: str):
        
        command = f'SELECT * FROM {self.SETTINGS_TABLE} WHERE {self.GUILD_ID_COL}=? AND {self.MODULE_COL}=? AND {self.KEY_COL}=? LIMIT 1;'
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
            
            command = f'INSERT INTO {self.SETTINGS_TABLE} ({self.GUILD_ID_COL}, {self.MODULE_COL}, {self.KEY_COL}, {self.VALUE_COL}) VALUES (?, ?, ?, ?) ON CONFLICT({self.GUILD_ID_COL}, {self.MODULE_COL}, {self.KEY_COL}) DO UPDATE SET {self.VALUE_COL}=excluded.{self.VALUE_COL};'
            task = (int(guild_id), str(module), str(key), value)
        
            cur = self.conn.cursor()
            cur.execute(command, task)
            self.conn.commit()
        
        except Error as e:
            self.logger.error("DB",e)
            