import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import TOKEN
from database import events_df, subscribe, export_csv, start
import pandas as pd

# Bot and database setup
DATABASE_URI = 'sqlite:///subscriptions.db'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handlers
start_handler = CommandHandler('start', start)
events_handler = CommandHandler('events', events)
subscribe_handler = CommandHandler('subscribe', subscribe, pass_args=True)
export_csv_handler = CommandHandler('export_csv', export_csv)

# Adding handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(events_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(export_csv_handler)

# Start the bot
updater.start_polling()
updater.idle()
