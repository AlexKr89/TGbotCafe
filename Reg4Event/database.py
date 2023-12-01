# database.py
import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_filename, events_filename):
        self.db_filename = db_filename
        self.events_filename = events_filename
        self.create_tables()
        self.load_events()

    def create_tables(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                event_date DATE NOT NULL,
                event_time TIME NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                user_info TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        ''')
        conn.commit()
        conn.close()

    def load_events(self):
        events = pd.read_excel(self.events_filename)
        conn = sqlite3.connect(self.db_filename)
        events.to_sql('events', conn, index=False, if_exists='replace')
        conn.close()

    def get_events(self):
        conn = sqlite3.connect(self.db_filename)
        query = 'SELECT id, event_name, event_date, event_time FROM events'
        events = pd.read_sql(query, conn)
        conn.close()
        return events

    def save_registration(self, event_id, user_info):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO registrations (event_id, user_info) VALUES (?, ?)', (event_id, user_info))
        conn.commit()
        conn.close()
