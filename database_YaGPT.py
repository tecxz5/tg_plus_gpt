import sqlite3
import logging

class Tokens:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
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

    def create_user_profile(self, chat_id):
        # cоздаем "профиль" с 4 сессиями и 500 токенами в каждой сессии
        self.cursor.execute("INSERT OR IGNORE INTO sessions (chat_id, sessions_count, tokens) VALUES (?, ?, ?)", (chat_id, 4, 1000))
        self.cursor.execute("INSERT OR IGNORE INTO tokens_used (chat_id, tokens_used) VALUES (?, ?)", (chat_id, 0))
        self.conn.commit()

    def reset_session(self, chat_id):
        # уменьшаем количество сессий на 1 и сбрасываем кол-во токенов до 500
        self.cursor.execute("UPDATE sessions SET sessions_count = sessions_count - 1, tokens = 1000 WHERE chat_id = ?",
                            (chat_id,))
        self.conn.commit()

    def get_user_data(self, chat_id):
        self.cursor = self.conn.cursor()
        result = self.cursor.fetchone()
        if result:
            return {
                'chat_id': result[0],
                'sessions_count': result[1],
                'tokens': result[2]
            }
        return None

    def deduct_tokens(self, chat_id, tokens_count):
        logging.info(f"Отнимаем {tokens_count} токенов у пользователя {chat_id}")
        self.cursor.execute("UPDATE sessions SET tokens = tokens - ? WHERE chat_id = ?", (tokens_count, chat_id))
        self.conn.commit()

    def update_tokens_used(self, chat_id, tokens_count):
        logging.info(f"Добавляем {tokens_count} использованных токенов пользователю {chat_id}")
        # обновляем общее количество использованных токенов
        self.cursor.execute("UPDATE tokens_used SET tokens_used = tokens_used + ? WHERE chat_id = ?", (tokens_count, chat_id))
        self.conn.commit()

    def get_tokens(self, chat_id):
        # получение кол-ва доступных токенов
        self.cursor.execute("SELECT tokens FROM sessions WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def check_session(self, chat_id):
        self.cursor.execute("SELECT sessions_count FROM sessions WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def get_tokens_used(self, chat_id):
        # получение кол-ва использованных токенов
        self.cursor.execute("SELECT tokens_used FROM tokens_used WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0