# bot.py
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from database import Database, RegistrationDatabase

db = Database('events.xlsx')
registration_db = RegistrationDatabase('registrations.xlsx')

SELECT_EVENT, CONFIRMATION, USER_NAME, USER_PHONE = range(4)

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
    if query:
        context.user_data['selected_event'] = int(query.data)
        event = db.get_events()[context.user_data['selected_event']]
        formatted_date = event[1].strftime("%d.%m.%Y")
        formatted_time = event[2].strftime("%H:%M")
        confirmation_message = f"Вы хотите записаться на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}?"

        keyboard = [[InlineKeyboardButton("Да", callback_data='yes'),
                     InlineKeyboardButton("Нет", callback_data='no')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.message:
            query.edit_message_text(confirmation_message, reply_markup=reply_markup)
        else:
            update.message.reply_text(confirmation_message, reply_markup=reply_markup)

        return CONFIRMATION
    else:
        update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        return ConversationHandler.END

def confirmation(update: Update, context: CallbackContext) -> int:
    user_choice = update.callback_query.data
    event = db.get_events()[context.user_data['selected_event']]

    if user_choice == 'yes':
        update.message.reply_text("Для успешной записи, введите ваше ФИО")
        return USER_NAME
    else:
        update.message.reply_text("Вы отменили запись на мероприятие.")
        return ConversationHandler.END

def user_info(update: Update, context: CallbackContext) -> int:
    user_info = update.message.text
    context.user_data['user_info'] = user_info

    event = db.get_events()[context.user_data['selected_event']]
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = datetime.combine(datetime.today(), event[2]).strftime("%H:%M")
    confirmation_message = f"Вы успешно записаны на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}\n\nВаши данные:\n{user_info}"

    # Сохраняем данные о регистрации в базу данных
    registration_db.save_registration(event[0], user_info)

    if 'callback_query' in context.user_data and context.user_data['callback_query']:
        query = context.user_data['callback_query']
        if query.message:
            query.edit_message_text(confirmation_message)
        else:
            update.message.reply_text(confirmation_message)
    else:
        update.message.reply_text(confirmation_message)

    return ConversationHandler.END

def enter_name(update: Update, context: CallbackContext) -> int:
    context.user_data['user_name'] = update.message.text
    event = db.get_events()[context.user_data['selected_event']]
    query = update.callback_query
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = event[2].strftime("%H:%M")
    confirmation_message = f"Вы хотите записаться на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}?\n\nВаше ФИО: {context.user_data['user_name']}"
    
    keyboard = [[InlineKeyboardButton("Да", callback_data='yes'),
                 InlineKeyboardButton("Нет", callback_data='no')]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(confirmation_message, reply_markup=reply_markup)
    return USER_PHONE

def enter_phone(update: Update, context: CallbackContext) -> int:
    context.user_data['user_phone'] = update.message.text
    event = db.get_events()[context.user_data['selected_event']]
    query = update.callback_query
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = datetime.combine(datetime.today(), event[2]).strftime("%H:%M")
    confirmation_message = f"Вы успешно записаны на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}\n\nВаши данные:\nФИО: {context.user_data['user_name']}\nКонтактный телефон: {context.user_data['user_phone']}"

    # Сохраняем данные о регистрации в базу данных
    registration_db.save_registration(event[0], f"{context.user_data['user_name']}, {context.user_data['user_phone']}")

    query.edit_message_text(confirmation_message)
    return ConversationHandler.END

def test_registration(update: Update, context: CallbackContext) -> None:
    # Эта функция предназначена только для тестирования процесса регистрации
    event_name = "Танцы"  
    user_name = "Пупа Лупа"  
    user_phone = "89182547412"

    # Сохраняем регистрацию
    registration_db.save_registration(event_name, f"{user_name}, {user_phone}")

    update.message.reply_text("Тестирование регистрации завершено!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_EVENT: [CallbackQueryHandler(select_event)],
            CONFIRMATION: [CallbackQueryHandler(confirmation)],
            USER_NAME: [MessageHandler(Filters.text & ~Filters.command, enter_name)],
            USER_PHONE: [MessageHandler(Filters.text & ~Filters.command, enter_phone)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # Добавляем обработчик команды для тестирования регистрации
    dp.add_handler(CommandHandler('test_registration', test_registration))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
