import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER NOT NULL,
                              full_name TEXT NOT NULL,
                              message TEXT NOT NULL)''')
        self.conn.commit()

    def save_message(self, user_id, full_name, message):
        self.cursor.execute('INSERT INTO messages (user_id, full_name, message) VALUES (?,?,?)',
                            (user_id, full_name, message))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()