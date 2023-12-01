# bot.py
from datetime import datetime, time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TOKEN
from database import Database

# Загружаем токен и создаем экземпляр Database
db = Database('events.xlsx')

def start(update: Update, context: CallbackContext) -> None:
    events = db.get_events()
    message = "Доступные мероприятия:\n"
    for event_name, event_date, event_time in events:
        formatted_date = event_date.strftime("%d.%m.%Y")
        
        # Проверяем, является ли event_time строкой (в случае строки преобразуем в объект time)
        if isinstance(event_time, str):
            event_time = datetime.strptime(event_time, "%H:%M").time()
        
        formatted_time = event_time.strftime("%H:%M")
        message += f"{event_name}: {formatted_date} {formatted_time}\n"
    update.message.reply_text(message)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
