import sqlite3
from sqlite3 import Error

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Создание класса обработчика событий
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == 'sarafan_bot.db':
            process_changes()

def process_changes():
    # create a new connection
    conn = create_connection()
    if conn is not None:
        print(f"\nОбнаружены изменения! Вот обновленные данные:\n")
        select_all_orders(conn)
        close_connection(conn)
    else: 
        print("Невозможно подключиться к базе данных")

# Создание экземпляра класса Observer
observer = Observer()

def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect('sarafan_bot.db')
        print(f'successful connection with sqlite version {sqlite3.version}')
    except Error as e:
        print(e)
    return conn

def close_connection(conn):
    if conn:
        try:
            conn.close()
            print('connection closed')
        except Error as e:
            print(e)

def create_table(conn):
    try:
        query = '''CREATE TABLE IF NOT EXISTS orders 
                    (id integer PRIMARY KEY AUTOINCREMENT,
                    name text NOT NULL,
                    surname text NOT NULL,
                    phone text,
                    food text,
                    datetime text);'''
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        print('Table created')
    except Error as e:
        print(e)

def insert_order(conn, order):
    try:
        query = '''INSERT INTO orders(name, surname, phone, food, datetime) 
                   VALUES(?,?,?,?, strftime('%d.%m.%Y %H:%M', datetime('now', '+3 hour')))'''
        cursor = conn.cursor()
        cursor.execute(query, order)
        conn.commit()
        print('Order inserted')
    except Error as e:
        print(e)

def select_all_orders(conn):
    try:
        query = '''SELECT * FROM orders'''
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for row in rows:
            print(row)
    except Error as e:
        print(e)

if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)

    event_handler = FileChangeHandler()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        close_connection(conn)
