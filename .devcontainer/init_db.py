import sqlite3
from sqlite3 import Error

conn = None
try:
    conn = sqlite3.connect("database.sqlite")
except Error as e:
    print(e)
finally:
    if conn:
        conn.close()

files = ["key.txt", "tenor.txt", "openai.txt"]
for file in files:
    tmp = open(file, "w+")
