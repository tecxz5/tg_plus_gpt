import sqlite3

db_name = 'SpeechKit.db'

class Database:
    def __init__(self, db_name=db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_database()

    def create_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                                chat_id INTEGER PRIMARY KEY,
                                token_count INTEGER DEFAULT 500
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                chat_id INTEGER,
                                request_text TEXT,
                                request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(chat_id) REFERENCES tokens(chat_id)
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS voice_choices (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                chat_id INTEGER,
                                voice_choice TEXT,
                                choice_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY(chat_id) REFERENCES tokens(chat_id)
                            )''')
        self.conn.commit()

    def add_user(self, chat_id, token_count=500):
        self.cursor.execute("INSERT OR IGNORE INTO tokens (chat_id, token_count) VALUES (?, ?)", (chat_id, token_count))
        self.conn.commit()

    def get_token_count(self, chat_id):
        self.cursor.execute("SELECT token_count FROM tokens WHERE chat_id = ?", (chat_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def update_token_count(self, chat_id, new_count):
        self.cursor.execute("UPDATE tokens SET token_count = ? WHERE chat_id = ?", (new_count, chat_id))
        self.conn.commit()

    def save_request(self, chat_id, request_text):
        self.cursor.execute("INSERT INTO requests (chat_id, request_text) VALUES (?, ?)", (chat_id, request_text))
        self.conn.commit()

    def save_voice_choice(self, chat_id, voice_choice):
        self.cursor.execute("INSERT INTO voice_choices (chat_id, voice_choice) VALUES (?, ?)", (chat_id, voice_choice))
        self.conn.commit()

    def get_chosen_voice(self, chat_id):
        self.cursor.execute(
            "SELECT voice_choice FROM voice_choices WHERE chat_id = ? ORDER BY choice_time DESC LIMIT 1", (chat_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def insert_row(user_id, message, cell, value, db_name=db_name):
        try:
            # Создаем подключение к базе данных
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                # Вставляем в таблицу сообщение и заполняем ячейку cell значением value
                cursor.execute(f'''INSERT INTO messages (user_id, message, {cell}) VALUES (?, ?, ?)''',
                               (user_id, message, value))
                # Сохраняем изменения
                conn.commit()
        except Exception as e:
            print(f"Error: {e}")

    def count_all_blocks(user_id, db_name=db_name):
        try:
            # Подключаемся к базе
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                # Считаем, сколько аудиоблоков использовал пользователь
                cursor.execute('''SELECT SUM(stt_blocks) FROM messages WHERE user_id=?''', (user_id,))
                data = cursor.fetchone()
                # Проверяем data на наличие хоть какого-то полученного результата запроса
                # И на то, что в результате запроса мы получили какое-то число в data[0]
                if data and data[0]:
                    # Если результат есть и data[0] == какому-то числу, то
                    return data[0]  # возвращаем это число - сумму всех потраченных аудиоблоков
                else:
                    # Результата нет, так как у нас ещё нет записей о потраченных аудиоблоках
                    return 0  # возвращаем 0
        except Exception as e:
            print(f"Error: {e}")

    def close(self):
        self.conn.close()