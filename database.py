import sqlite3

class Database:
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
        self.conn.close()

    def create_user_profile(self, chat_id):
        # cоздаем "профиль" с 4 сессиями и 500 токенами в каждой сессии
        self.cursor.execute("INSERT INTO users (chat_id, sessions_count, tokens) VALUES (?, ?, ?)", (chat_id, 4, 500))
        self.conn.commit()
        self.conn.close()

    def reset_session(self, chat_id):
        # уменьшаем количество сессий на 1 и сбрасываем кол-во токенов до 500
        self.cursor.execute("UPDATE users SET sessions_count = sessions_count - 1, tokens = 500 WHERE chat_id = ?",
                            (chat_id,))
        self.conn.commit()
        self.conn.close()

    def update_tokens_used(self, chat_id, tokens_used):
        # обновляем общее количество использованных токенов
        self.cursor.execute("UPDATE tokens_used SET total_tokens_used = total_tokens_used + ? WHERE chat_id = ?", (tokens_used, chat_id))
        self.conn.commit()
        self.conn.close()

    def get_tokens_used(self, chat_id):
        # получение кол-ва использованных токенов
        self.cursor.execute("SELECT total_tokens_used FROM tokens_used WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0
        self.conn.close()