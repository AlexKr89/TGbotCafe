import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TOKEN
from database import events_df, subscribe, export_csv, start  # Импортируем функцию start из модуля database

# Настройки бота
DATABASE_URI = 'sqlite:///subscriptions.db'

# Настройки логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализация бота и базы данных
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Обработка команд
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def events(update: Update, context: CallbackContext) -> None:
    event_list = "\n".join(events_df['event_name'])
    update.message.reply_text(f"Доступные мероприятия:\n{event_list}")

events_handler = CommandHandler('events', events)
dispatcher.add_handler(events_handler)

subscribe_handler = CommandHandler('subscribe', subscribe, pass_args=True)
dispatcher.add_handler(subscribe_handler)

export_csv_handler = CommandHandler('export_csv', export_csv)
dispatcher.add_handler(export_csv_handler)

# Запуск бота
updater.start_polling()
updater.idle()
