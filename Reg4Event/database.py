import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                event_date DATE NOT NULL,
                event_time TIME NOT NULL,
                user_info TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def get_events(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT event_name, event_date, event_time FROM registrations')
        events = cursor.fetchall()
        conn.close()
        return events