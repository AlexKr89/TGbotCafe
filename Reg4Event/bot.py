import logging
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pandas as pd
from sqlalchemy import create_engine
from config import TOKEN

# Настройки бота
DATABASE_URI = 'sqlite:///subscriptions.db'  # URI для SQLite, можно изменить на другую базу данных

# Настройки логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализация бота и базы данных
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
engine = create_engine(DATABASE_URI, echo=True)
conn = engine.connect()

# Создание таблицы подписок, если она не существует
conn.execute('''
CREATE TABLE IF NOT EXISTS subscriptions (
    chat_id INTEGER,
    event_name TEXT,
    PRIMARY KEY (chat_id, event_name)
);
''')

# Загрузка мероприятий из XLS файла
events_df = pd.read_excel('events.xlsx')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Этот бот предоставляет информацию о мероприятиях. '
                              'Используйте /events, чтобы увидеть доступные мероприятия.')

def events(update: Update, context: CallbackContext) -> None:
    event_list = "\n".join(events_df['event_name'])
    update.message.reply_text(f"Доступные мероприятия:\n{event_list}")

def subscribe(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    event_name = context.args[0]

    # Проверка наличия мероприятия
    if event_name not in events_df['event_name'].values:
        update.message.reply_text(f"Мероприятия {event_name} не существует.")
        return

    # Подписка пользователя
    conn.execute('INSERT OR IGNORE INTO subscriptions (chat_id, event_name) VALUES (?, ?)', (chat_id, event_name))
    update.message.reply_text(f"Вы подписались на мероприятие {event_name}.")

def export_csv(update: Update, context: CallbackContext) -> None:
    df = pd.read_sql('SELECT * FROM subscriptions', engine)
    df.to_csv('subscriptions.csv', index=False)
    update.message.reply_text("Экспорт подписок в CSV завершен.")

# Обработка команд
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

events_handler = CommandHandler('events', events)
dispatcher.add_handler(events_handler)

subscribe_handler = CommandHandler('subscribe', subscribe, pass_args=True)
dispatcher.add_handler(subscribe_handler)

export_csv_handler = CommandHandler('export_csv', export_csv)
dispatcher.add_handler(export_csv_handler)

# Запуск бота
updater.start_polling()
updater.idle()
