import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TOKEN
from database import events_df, subscribe, export_csv, start

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
    keyboard = []

    for index, row in events_df.iterrows():
        event_name = row['event_name']
        event_date = row['event_date']

        # Отображение event_date и кнопки "Записаться"
        text = f"{event_name}\nДата: {event_date}"
        button = InlineKeyboardButton("Записаться", callback_data=f"subscribe_{index}")
        keyboard.append([text, button])

    # Создание клавиатуры с кнопками
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Доступные мероприятия:", reply_markup=reply_markup)

events_handler = CommandHandler('events', events)
dispatcher.add_handler(events_handler)

subscribe_handler = CommandHandler('subscribe', subscribe, pass_args=True)
dispatcher.add_handler(subscribe_handler)

export_csv_handler = CommandHandler('export_csv', export_csv)
dispatcher.add_handler(export_csv_handler)

# Запуск бота
updater.start_polling()
updater.idle()
