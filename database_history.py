import sqlite3
from sqlite3 import Error
import datetime

class History:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)
        self.create_table()

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

    def create_table(self):
        try:
            sql_create_table = """ CREATE TABLE IF NOT EXISTS history (
                                            id integer PRIMARY KEY,
                                            user_id text NOT NULL,
                                            role text NOT NULL,
                                            message text NOT NULL,
                                            timestamp text NOT NULL
                                        ); """
            c = self.conn.cursor()
            c.execute(sql_create_table)
        except Error as e:
            print(e)

    def save_message(self, user_id, role, message):
        sql = ''' INSERT INTO history(user_id,role,message,timestamp)
                 VALUES(?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (user_id, role, message, datetime.datetime.now().isoformat()))
        self.conn.commit()