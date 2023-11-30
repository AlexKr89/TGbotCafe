# bot.py
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TOKEN
from database import Database

# Загружаем токен и создаем экземпляр Database
db = Database('events.xlsx')

def start(update: Update, context: CallbackContext) -> None:
    events = db.get_events()
    message = "Доступные мероприятия:\n"
    for event_name, event_date in events:
        formatted_date = event_date.strftime("%d.%m.%Y")
        message += f"{event_name}: {formatted_date}\n"
    update.message.reply_text(message)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
