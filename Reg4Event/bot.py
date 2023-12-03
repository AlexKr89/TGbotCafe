# bot.py
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from database import Database, RegistrationDatabase

db = Database('events.xlsx')
registration_db = RegistrationDatabase('registrations.xlsx')

SELECT_EVENT, CONFIRMATION, USER_INFO = range(3)
USER_PHONE = range(3, 5)

def start(update: Update, context: CallbackContext) -> int:
    events = db.get_events()
    message = "Доступные мероприятия:\n"
    for event_name, event_date, event_time in events:
        formatted_date = event_date.strftime("%d.%m.%Y")
        formatted_time = event_time.strftime("%H:%M")
        message += f"{event_name}: {formatted_date} {formatted_time}\n"

    keyboard = [[InlineKeyboardButton(event[0], callback_data=str(events.index(event))) for event in events]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(message, reply_markup=reply_markup)
    return SELECT_EVENT

def select_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data['selected_event'] = int(query.data)
    event = db.get_events()[context.user_data['selected_event']]
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = event[2].strftime("%H:%M")
    confirmation_message = f"Вы хотите записаться на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}?"

    keyboard = [[InlineKeyboardButton("Да", callback_data='yes'),
                 InlineKeyboardButton("Нет", callback_data='no')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(confirmation_message, reply_markup=reply_markup)
    return CONFIRMATION

def confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_choice = query.data
    event = db.get_events()[context.user_data['selected_event']]

    if user_choice == 'yes':
        query.edit_message_text("Для успешной записи, введите следующие данные:\nФИО")
        return USER_INFO
    else:
        query.edit_message_text("Вы отменили запись на мероприятие.")
        return ConversationHandler.END

def user_info(update: Update, context: CallbackContext) -> int:
    user_info = update.message.text
    context.user_data['user_info'] = user_info
    
    # Просим ввести номер телефона
    update.message.reply_text("Введите номер телефона для обратной связи:")
    
    return USER_PHONE

def continue_registration(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Для успешной записи, введите следующие данные:\nФИО")
    return USER_INFO

def enter_phone(update: Update, context: CallbackContext) -> int:
    user_phone = update.message.text
    context.user_data['user_phone'] = user_phone

    event = db.get_events()[context.user_data['selected_event']]
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = event[2].strftime("%H:%M")
    confirmation_message = f"Вы успешно записаны на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}\n\nВаши данные:\nФИО: {context.user_data['user_info']}\nНомер телефона: {user_phone}"

    # Сохраняем данные о регистрации в базу данных
    registration_db.save_registration(event[0], context.user_data['user_info'], user_phone)

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
            USER_INFO: [MessageHandler(Filters.text & ~Filters.command, user_info)],
            USER_PHONE: [MessageHandler(Filters.text & ~Filters.command, enter_phone)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()