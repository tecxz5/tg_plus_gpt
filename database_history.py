import sqlite3
from sqlite3 import Error
import datetime

class History:
    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            return conn
        except Error as e:
            print(e)

    def create_table(self, user_id):
        table_name = f"history_{user_id}"
        try:
            sql_create_table = f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                            id integer PRIMARY KEY,
                                            role text NOT NULL,
                                            message text NOT NULL,
                                            timestamp text NOT NULL
                                        ); """
            c = self.conn.cursor()
            c.execute(sql_create_table)
        except Error as e:
            print(e)

    def save_message(self, user_id, role, message):
        if role != 'system':
            table_name = f"history_{user_id}"
            # Используем f-строку для формирования запроса, корректно обрабатывая переменные
            sql = f''' INSERT INTO {table_name}(role,message,timestamp)
                    VALUES(?,?,?) '''
            cur = self.conn.cursor()
            # Используем параметризованный запрос для безопасной вставки значений
            cur.execute(sql, (role, message, datetime.datetime.now().isoformat()))
            self.conn.commit()