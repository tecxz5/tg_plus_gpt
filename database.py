import sqlite3, json

db_name = 'manager.db'

def create_connection(db_name):
    conn = sqlite3.connect(db_name)
    return conn

class SQL:
    def __init__(self):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)

    def create_user(self, id):
        story = {
            "user": "",
            "assistant": ""
        }
        self.conn.execute("""INSERT INTO users (id, history) VALUES (?, ?)""", (id, json.dumps(story)))

    def has_user(self, id):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("""SELECT * from users where id = ?""", (id,))
        rows = cursor.fetchall()
        return len(rows) != 0

    def set_level(self, id, level):
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE users set level=? WHERE id = ?""", (level, id))
        self.conn.commit()

    def set_ai(self, id, ai):
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE users set gptAI=? WHERE id = ?""", (ai, id))
        self.conn.commit()

    def set_gpt_history(self, id, text):
        cursor = self.conn.cursor()
        cursor.execute("""UPDATE users set history=? WHERE id = ?""", (text, id))
        self.conn.commit()

    def get_level(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT level from users where id = ?""", id)
        rows = cursor.fetchall()
        return rows

    def get_mode(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT gptAI from users where id = ?""", id)
        rows = cursor.fetchall()
        return rows

    def get_history(self, id):
        cursor = self.conn.cursor()
        cursor.execute("""SELECT history from users where id = ?""", (id,))
        rows = cursor.fetchall()
        return rows