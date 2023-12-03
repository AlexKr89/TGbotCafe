from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from config import TOKEN
from database import Database, RegistrationDatabase

db = Database('events.xlsx')
registration_db = RegistrationDatabase('registrations.xlsx')

SELECT_EVENT, CONFIRMATION, USER_INFO, USER_PHONE = range(4)

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

def user_info(update: Update, context: CallbackContext) -> int:
    # Обработка ввода ФИО
    user_info = update.message.text
    context.user_data['user_info'] = user_info

    # Предложим ввести номер телефона
    keyboard = [[InlineKeyboardButton("Продолжить", callback_data='continue')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Введите номер телефона для обратной связи", reply_markup=reply_markup)

    return USER_PHONE

def continue_registration(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Проверяем, является ли обновлением от callback_query или message
    if update.message:
        user_phone = update.message.text
    else:
        # Если обновление пришло от callback_query, то используем информацию из контекста
        user_phone = context.user_data.get('user_phone', '')

    # Сохраняем данные о регистрации в базу данных
    event = db.get_events()[context.user_data['selected_event']]
    formatted_date = event[1].strftime("%d.%m.%Y")
    formatted_time = event[2].strftime("%H:%M")
    confirmation_message = f"Вы успешно записаны на мероприятие:\n{event[0]} - {formatted_date} {formatted_time}\n\nВаши данные:\nФИО: {context.user_data['user_info']}\nНомер телефона: {user_phone}"

    registration_db.save_registration(event[0], f"{context.user_data['user_info']}, {user_phone}")

    context.bot.send_message(update.effective_chat.id, confirmation_message)

    return ConversationHandler.END


def test_registration(update: Update, context: CallbackContext) -> None:
    # Эта функция предназначена только для тестирования процесса регистрации
    event_name = "Танцы"  # Замените на реальное имя события
    user_info = "Пупа Лупа"  # Замените на реальную информацию о пользователе
    user_phone = "89182547412"  # Замените на реальный номер телефона

    # Сохраняем регистрацию
    registration_db.save_registration(event_name, f"{user_info}, {user_phone}")

    update.message.reply_text("Тестирование регистрации завершено!")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_EVENT: [CallbackQueryHandler(select_event)],
            CONFIRMATION: [CallbackQueryHandler(continue_registration)],
            USER_INFO: [MessageHandler(Filters.text & ~Filters.command, user_info)],
            USER_PHONE: [MessageHandler(Filters.text & ~Filters.command, continue_registration)]
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
