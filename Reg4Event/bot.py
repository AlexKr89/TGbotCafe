from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from database import Database
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

db = Database('registration.db', 'events.xlsx')

SELECT_EVENT, CONFIRMATION, USER_INFO = range(3)

def start(update: Update, context: CallbackContext) -> int:
    events = db.get_events()
    message = "Доступные мероприятия:\n"
    for _, event in events.iterrows():
        event_name = event['event_name']
        
        # Check if 'event_date' and 'event_time' columns are datetime64 dtype
        if is_datetime64_any_dtype(event['event_date']):
            event_date = event['event_date'].strftime("%d.%m.%Y")
        else:
            event_date = "Нет данных о дате"

        if is_datetime64_any_dtype(event['event_time']):
            event_time = event['event_time'].strftime("%H:%M")
        else:
            event_time = "Нет данных о времени"

        message += f"{event_name}: {event_date} {event_time}\n"

    keyboard = [[InlineKeyboardButton(event['event_name'], callback_data=str(event['id'])) for _, event in events.iterrows()]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(message, reply_markup=reply_markup)
    return SELECT_EVENT

def select_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data['selected_event'] = int(query.data)
    event = db.get_events().loc[context.user_data['selected_event']]
    formatted_date = event['event_date'].strftime("%d.%m.%Y")

    formatted_time = event['event_time'].strftime("%H:%M") if not pd.isnat(event['event_time']) else "Нет данных о времени"


    confirmation_message = f"Вы хотите записаться на мероприятие:\n{event['event_name']} - {formatted_date} {formatted_time}?"

    keyboard = [[InlineKeyboardButton("Да", callback_data='yes'),
                 InlineKeyboardButton("Нет", callback_data='no')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(confirmation_message, reply_markup=reply_markup)
    return CONFIRMATION

def confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_choice = query.data
    event = db.get_events().loc[context.user_data['selected_event']]

    if user_choice == 'yes':
        query.edit_message_text("Для успешной записи, введите следующие данные:\nФИО, Контактный телефон")
        return USER_INFO
    else:
        query.edit_message_text("Вы отменили запись на мероприятие.")
        return ConversationHandler.END

def user_info(update: Update, context: CallbackContext) -> int:
    user_info = update.message.text
    context.user_data['user_info'] = user_info

    event = db.get_events().loc[context.user_data['selected_event']]
    formatted_date = event['event_date'].strftime("%d.%m.%Y")
    formatted_time = event['event_time'].strftime("%H:%M")
    confirmation_message = f"Вы успешно записаны на мероприятие:\n{event['event_name']} - {formatted_date} {formatted_time}\n\nВаши данные:\n{user_info}"

    # Сохраняем данные о регистрации в базу данных
    db.save_registration(context.user_data['selected_event'], user_info)

    update.message.reply_text(confirmation_message)
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_EVENT: [CallbackQueryHandler(select_event)],
            CONFIRMATION: [CallbackQueryHandler(confirmation)],
            USER_INFO: [MessageHandler(Filters.text & ~Filters.command, user_info)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
