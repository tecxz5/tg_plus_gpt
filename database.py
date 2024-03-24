# database_manager.py
import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                chat_id INTEGER PRIMARY KEY,
                sessions_count INTEGER,
                tokens INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens_used (
                chat_id INTEGER PRIMARY KEY,
                tokens_used INTEGER
            )
        """)
        self.conn.commit()

    def add_new_session(self, chat_id):
        self.cursor.execute("INSERT INTO sessions (chat_id, sessions_count, tokens) VALUES (?, ?, ?) ON CONFLICT(chat_id) DO UPDATE SET sessions_count = sessions_count + 1, tokens = 1000", (chat_id, 1, 1000))
        self.conn.commit()

    def update_tokens_used(self, chat_id, tokens_used):
        self.cursor.execute("UPDATE tokens_used SET tokens_used = ? WHERE chat_id = ?", (tokens_used, chat_id))
        self.conn.commit()

    def get_tokens_used(self, chat_id):
        self.cursor.execute("SELECT tokens_used FROM tokens_used WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def check_sessions_count(self, chat_id):
        self.cursor.execute("SELECT sessions_count FROM sessions WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.conn.close()