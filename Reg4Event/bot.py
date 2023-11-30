# database.py
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URI = 'sqlite:///subscriptions.db'

# Инициализация базы данных
engine = create_engine(DATABASE_URI, echo=True)
conn = engine.connect()

# Создание таблицы подписок, если она не существует
create_table_query = text('''
CREATE TABLE IF NOT EXISTS subscriptions (
    chat_id INTEGER,
    event_name TEXT,
    PRIMARY KEY (chat_id, event_name)
);
''')

conn.execute(create_table_query)

# Загрузка мероприятий из XLS файла
events_df = pd.read_excel('/D:/Work/Git/Reg4Event/events.xlsx', engine='openpyxl')

def subscribe(update, context):
    chat_id = update.message.chat_id
    event_name = context.args[0]

    # Проверка наличия мероприятия
    if event_name not in events_df['event_name'].values:
        update.message.reply_text(f"Мероприятия {event_name} не существует.")
        return

    # Подписка пользователя
    conn.execute('INSERT OR IGNORE INTO subscriptions (chat_id, event_name) VALUES (?, ?)', (chat_id, event_name))
    update.message.reply_text(f"Вы подписались на мероприятие {event_name}.")

def export_csv(update, context):
    df = pd.read_sql('SELECT * FROM subscriptions', engine)
    df.to_csv('subscriptions.csv', index=False)
    update.message.reply_text("Экспорт подписок в CSV завершен.")

def start(update, context):
    update.message.reply_text('Привет! Этот бот предоставляет информацию о мероприятиях. '
                              'Используйте /events, чтобы увидеть доступные мероприятия.')
