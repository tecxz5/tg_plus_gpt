import sqlite3

db_name = 'bot_database.db' # Исправлено имя файла базы данных

def create_connection(db_name):
    conn = sqlite3.connect(db_name)
    return conn

def create_database():
    conn = create_connection(db_name)
    cursor = conn.cursor()

    # Создание таблицы для хранения информации о пользователях
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            subject TEXT,
            explanation_level TEXT,
            task TEXT,
            gpt_response TEXT
        )
    """)

    # Создание таблицы для хранения выбранных предметов и уровней объяснения
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subject_level (
            user_id INTEGER PRIMARY KEY,
            subject TEXT,
            level TEXT
        )
    """)

    conn.commit()
    conn.close()

def add_user_data(user_id, subject, explanation_level, task, gpt_response, db_name):
    conn = create_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_data (user_id, subject, explanation_level, task, gpt_response) VALUES (?, ?, ?, ?, ?)",
                   (user_id, subject, explanation_level, task, gpt_response))
    conn.commit()
    conn.close()

def update_user_data(user_id, db_name, subject=None, explanation_level=None, task=None, gpt_response=None):
    conn = create_connection(db_name)
    cursor = conn.cursor()
    set_values = ', '.join([f"{column} = ?" for column in ['subject', 'explanation_level', 'task', 'gpt_response'] if locals()[column] is not None])
    cursor.execute(f"UPDATE user_data SET {set_values} WHERE user_id = ?", (subject, explanation_level, task, gpt_response, user_id))
    conn.commit()
    conn.close()

def get_user_data(user_id, db_name):
    conn = create_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def save_subject_and_level(user_id, subject, level, db_name):
    conn = create_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_subject_level (user_id, subject, level) VALUES (?, ?, ?)", (user_id, subject, level))
    conn.commit()
    conn.close()