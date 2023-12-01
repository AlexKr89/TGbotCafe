# database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_filename, events_filename):
        self.db_filename = db_filename
        self.events_filename = events_filename
        self.create_tables()

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
        wb = openpyxl.load_workbook(self.events_filename)
        sheet = wb.active
        events = [(row[0], row[1], row[2]) for row in sheet.iter_rows(min_row=2, values_only=True) if row[0] and row[1] and row[2]]
        wb.close()

        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO events (event_name, event_date, event_time) VALUES (?, ?, ?)', events)
        conn.commit()
        conn.close()

    def get_events(self):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('SELECT id, event_name, event_date, event_time FROM events')
        events = cursor.fetchall()
        conn.close()
        return events

    def save_registration(self, event_id, user_info):
        conn = sqlite3.connect(self.db_filename)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO registrations (event_id, user_info) VALUES (?, ?)', (event_id, user_info))
        conn.commit()
        conn.close()
