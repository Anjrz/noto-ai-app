import sqlite3

class Database:
    def __init__(self, db_path='notoai.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                premium INTEGER DEFAULT 0,
                notes_this_month INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def register_user(self, username, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        return cursor.fetchone() is not None
